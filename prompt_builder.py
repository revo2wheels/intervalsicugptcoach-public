#prompt_builder.py

from coaching_profile import REPORT_CONTRACT, REPORT_RESOLUTION, RENDERER_PROFILES
from textwrap import dedent

def build_system_prompt_from_header(report_type: str, header: dict) -> str:
    """
    Build deterministic renderer instructions for GPT based on the
    URF v5.1 report contract.

    This output is DATA ONLY and must be used as a system-role message
    by the caller.
    """
    from coaching_profile import RENDERER_PROFILES
    from textwrap import dedent

    title = header.get("title", f"{report_type.title()} Report")
    scope = header.get("scope", "Training and wellness summary")
    sources = header.get("data_sources", "Intervals.icu activity and wellness datasets")
    intended = header.get("intended_use", "General endurance coaching insight")
    contract_sections = REPORT_CONTRACT.get(report_type, [])
    contract_version = "URF v5.1"

    # --------------------------------------------------
    # Resolve section order from contract
    # --------------------------------------------------
    if isinstance(contract_sections, dict):
        section_order = list(contract_sections.keys())
    else:
        section_order = contract_sections or ["Summary", "Metrics", "Actions"]

    manifest_lines = [f"{i}. {section}" for i, section in enumerate(section_order, start=1)]

    # --------------------------------------------------
    # Resolve renderer profiles
    # --------------------------------------------------
    global_profile = RENDERER_PROFILES.get("global", {})
    report_profile = RENDERER_PROFILES.get(report_type, {})

    stack_structure = report_profile.get("stack_structure", {})

    hard_rules = global_profile.get("hard_rules", [])
    list_rules = global_profile.get("list_rules", [])
    tone_rules = global_profile.get("tone_rules", [])

    interpretation_rules = report_profile.get("interpretation_rules", [])
    allowed_enrichment = report_profile.get("allowed_enrichment", [])

    coaching_cfg = report_profile.get("coaching_sentences", {})
    coaching_enabled = coaching_cfg.get("enabled", False)
    coaching_max = coaching_cfg.get("max_per_section", 0)

    section_handling = report_profile.get("section_handling", {})
    stack_labels = report_profile.get("stack_labels", {})
    signal_hierarchy = report_profile.get("signal_hierarchy", [])
    fatigue_logic = report_profile.get("fatigue_logic", [])
    question_themes = report_profile.get("question_rule", [])
    events_rule = report_profile.get("events_rule")
    planned_events_rule = report_profile.get("planned_events_rule")
    resolution = REPORT_RESOLUTION.get(report_type, {})

    # ➕ NEW: presentation config (read directly, no helpers)
    state_presentation = global_profile.get("state_presentation", {})
    emphasis = report_profile.get("emphasis", {})
    framing = report_profile.get("framing", {})
    closing_cfg = report_profile.get("closing_note", {})
    post_render = report_profile.get("post_render", {})

    # --------------------------------------------------
    # Optional blocks (existing)
    # --------------------------------------------------

    stack_map_lines = []

    for layer, sections in stack_structure.items():
        label = stack_labels.get(layer, layer.upper())

        for section in sections:
            stack_map_lines.append(f"{section} → {label}")
    #-----------------------------------------------------------------
    stack_lines = []
    for layer, sections in stack_structure.items():
        label = stack_labels.get(layer, layer.upper())

        stack_lines.append(label)
        for s in sections:
            stack_lines.append(f"- {s}")
    #-----------------------------------------------------------------
    stack_block = ""
    if stack_structure:

        stack_lines = []

        for layer, sections in stack_structure.items():

            layer_name = layer.replace("_", " ").title()

            stack_lines.append(f"{layer_name}:")
            for s in sections:
                stack_lines.append(f"- {s}")

            stack_lines.append("")

        stack_block = dedent(f"""
        STACK STRUCTURE RULE:

        The report MUST be organised into the following conceptual intelligence layers:

        {chr(10).join(stack_lines)}

        These layers are PRESENTATIONAL GROUPINGS ONLY.

        They must NOT:
        - change section order
        - override section_handling rules
        - modify interpretation_rules
        - alter table rendering rules

        Sections must appear in the exact URF contract order.
        Stack layers only determine which layer header a section appears under.

        Each section must appear under its corresponding stack layer while still following the URF section order.
        A stack layer header MUST be rendered once when the first section belonging to that layer appears.
        Subsequent sections mapped to the same stack layer MUST remain under that header and MUST NOT repeat the header.
        """).strip()
    #-----------------------------------------------------------------
    stack_map_block = ""

    if stack_map_lines:
        stack_map_block = dedent(f"""
        STACK SECTION MAP:
        {chr(10).join(stack_map_lines)}
        """).strip()

    resolution_block = ""
    #-----------------------------------------------------------------
    if resolution:
        resolution_block = dedent(f"""
        DATA RESOLUTION MODEL:

        This report uses the following semantic resolution rules.

        {chr(10).join(f"- {k}: {v}" for k, v in resolution.items())}

        These rules determine which metrics are authoritative,
        which signals may appear, and the time horizon used
        for interpretation.

        Resolution rules MUST NOT be printed in the report output.
        """).strip()
    #-----------------------------------------------------------------
    section_handling_block = ""
    if section_handling:
        section_handling_block = dedent(f"""
        SECTION HANDLING RULES:
        {chr(10).join(f"- {k}: {v}" for k, v in section_handling.items())}

        Handling meanings:

        - full:
            Render the entire section exactly as provided.
            Tables remain tables, lists remain lists.
            Do not remove rows or fields.

        - summary:
            Render a compact representation using ONLY existing semantic aggregates
            already present in the section. Do NOT derive new metrics.

        Summary rules:
            Prefer a short table if aggregate values exist.
            If aggregates do not exist, show the top-level fields only.
            Do NOT iterate full arrays or lists.
            Do NOT narrate each element of a list.
            Maximum 3–5 rows or key metrics.

        - table_summary:
            Render a condensed table using aggregate fields only.
            Do NOT render the full underlying dataset.

        - headline:
            Render only the primary indicators of the section.
            Maximum 3–4 metrics.
            No tables longer than one row.
            No subsections.
            No detailed narrative.

        Rules:
        • Maximum 5 rows.
        • Prefer totals, means, or trend indicators already provided.
        • Do NOT derive calculations.

        - forbid:
        This section MUST NOT be rendered in the report output.
        It may still be used internally for reasoning.
        """).strip()
    #-----------------------------------------------------------------
    closing_note_block = ""

    if closing_cfg.get("required"):
        verdict_rule = closing_cfg.get("verdict_rule", "")
        classifications = closing_cfg.get("classification_required", [])
        focus = closing_cfg.get("focus", "")
        intent = closing_cfg.get("intent_rule", "")
        anchors = closing_cfg.get("anchor_metrics", [])
        exact_sent = closing_cfg.get("exact_sentences")
        max_sent = closing_cfg.get("max_sentences")
        sentence_structure = closing_cfg.get("sentence_structure", [])

        closing_note_block = dedent(f"""
        CLOSING NOTE REQUIREMENTS:
        - The closing note MUST begin with one of the following classifications:
        {", ".join(classifications)}.
        - {verdict_rule}
        - The closing note MUST remain within the conceptual focus: {focus}.
        - {intent}
        - It MUST anchor strictly to: {", ".join(anchors)}.
        - It MUST NOT introduce new metrics or reinterpret semantic data.
        """).strip()

        if exact_sent:
            closing_note_block += f"\n- The closing note MUST contain exactly {exact_sent} sentences."
        elif max_sent:
            closing_note_block += f"\n- Maximum {max_sent} sentences."

        if sentence_structure:
            closing_note_block += "\n- The six sentences MUST follow this structure:"
            for s in sentence_structure:
                closing_note_block += f"\n  {s}"
    #-----------------------------------------------------------------
    # WHAT NEXT: the decision translated onto the athlete's planned sessions.
    # Replaces the open Closing Reflection question where a profile enables it.
    what_next_enabled = report_profile.get("what_next", {}).get("enabled", False)
    what_next_block = ""

    if what_next_enabled:
        what_next_block = dedent("""
        WHAT NEXT (REQUIRED):
        At the end of the report (after the closing note, if there is one), render a section headed "What next" with exactly these three lines, in this order:
        - Today: whether to keep, adjust or reduce today's planned session, naming the session. If nothing is planned today, say so.
        - Next days: whether any planned sessions in the coming days should change, naming them, or state that no changes are needed.
        - Why: the one or two signals that drive this, in plain words.

        WHAT NEXT RULES:
        - "Today" is the date of meta.generated_at.local. If meta.period ends more than one day before that date, the report covers an earlier week: give only the Why line.
        - Restate the final directive; never form a different decision. Final directive precedence: training_guidance > adaptive_summary.taper_governance.recommended_adjustment > adaptive_summary.directive.
        - Use only planned sessions present in the data (planned_summary_by_date, planned_events_7d, events, future_actions, planned_summary_by_iso_week). Never invent a session, date, duration or number.
        - Translate engine labels into plain words (for example, overridden_by_phase means the plan's phase takes priority over what the athlete could handle today).
        - One sentence per line. Do not add a separate Closing Reflection section.
        """).strip()

    #-----------------------------------------------------------------
    post_render_block = ""

    post_cfg = report_profile.get("post_render", {}).get("explore_deeper", {})

    if post_cfg.get("enabled"):
        commands = post_cfg.get("commands", [])

        post_render_block = dedent(f"""
        POST-RENDER INTERACTION:
        - After the full report is rendered, present follow-up commands to allow deeper inspection.
        - These commands MUST be shown after the closing reflection section.
        - The commands MUST be rendered as short, copyable user prompts in raw markdown
        - Do NOT add explanation, narrative, or coaching around these commands.

        Suggested follow up questions:
        {chr(10).join([f'- "{cmd}"' for cmd in commands])}
        """).strip()

        if what_next_enabled:
            post_render_block = post_render_block.replace(
                "after the closing reflection section", "after the What next section"
            )
            post_render_block += (
                "\n- If actions contains a reflection, show its question first in this list,"
                " worded as the athlete would ask it."
            )
    #-----------------------------------------------------------------
    coaching_block = ""
    if coaching_enabled and coaching_max > 0:
        coaching_block = dedent(f"""
        COACHING INTERPRETATION RULES:
        - You are an Endurance Coach
        - You MAY include up to {coaching_max} short coaching sentence(s) per section.
        - Coaching sentences MUST be directly anchored to values, states, or interpretation fields in that section.
        - Coaching sentences MUST be descriptive or conditional, not predictive.
        - Coaching sentences MUST appear immediately after the section’s data and before the next divider.
        - Coaching sentences MUST NOT introduce new metrics.
        """).strip()

    #-----------------------------------------------------------------
    question_block = ""
    if coaching_enabled and question_themes and not what_next_enabled:
        question_block = dedent(f"""
        CLOSING REFLECTION RULE:
        After the full report is produced, generate exactly ONE short reflective coaching question.

        The question MUST be based on the dominant signal in the report.

        Allowed reflection themes:
        {chr(10).join(f"- {t}" for t in question_themes)}

        The closing question must be grounded in the signals present in the report
        and must not introduce new metrics or predictions.

        Format exactly as:
        ---
        Closing Reflection
        <question>
        """).strip()
    #-----------------------------------------------------------------
    enrichment_block = ""
    if allowed_enrichment:
        enrichment_block = dedent(f"""
        ALLOWED ENRICHMENT:
        {chr(10).join(f"- {r}" for r in allowed_enrichment)}
        """).strip()
    #-----------------------------------------------------------------
    events_block = ""

    if events_rule:
        icon_list = "\n".join(
            f"{i+1}) {icon}" for i, icon in enumerate(events_rule.get("icons", []))
        )

        duration_rules = "\n".join(f"- {r}" for r in events_rule.get("duration_conversion", []))
        rules = "\n".join(f"- {r}" for r in events_rule.get("rules", []))

        columns = " | ".join(events_rule.get("column_order", []))

        events_block = dedent(f"""
        EVENTS (WEEKLY — NON-NEGOTIABLE):
        {rules}

        - The EVENTS table MUST use the following column order:
        {columns}

        {duration_rules}

        - When multiple icons apply, they MUST be rendered together in the following fixed order (left → right):
        {icon_list}
        """).strip()
    #-----------------------------------------------------------------
    planned_events_block = ""

    if planned_events_rule:
        planned_events_block = dedent(f"""
        PLANNED EVENTS (WEEKLY — NON-NEGOTIABLE):
        {chr(10).join(f"- {r}" for r in planned_events_rule)}
        """).strip()

    # --------------------------------------------------
    state_presentation_block = ""
    if state_presentation.get("enabled"):
        state_presentation_block = dedent(f"""
        STATE PRESENTATION:
        - Present a concise, single-sentence state banner at the top of the report.
        - Use ONLY semantic states already present in the data.
        - Do NOT derive, compute, or infer new states.
        - Style: {state_presentation.get("style")}
        """).strip()
    #-----------------------------------------------------------------
    emphasis_block = ""
    if emphasis:
        emphasis_block = dedent(f"""
        EMPHASIS GUIDANCE:
        The following sections should receive proportional narrative and visual emphasis.
        This does NOT change section order, inclusion, or data fidelity.
        {chr(10).join(f"- {k}: {v}" for k, v in emphasis.items())}
        """).strip()
    #-----------------------------------------------------------------
    framing_block = ""
    if framing:
        framing_block = dedent(f"""
        FRAMING INTENT:
        - Interpret and summarise this report through the following intent:
          {framing.get("intent")}
        - This intent guides prioritisation and narrative focus only.        
        """).strip()

    #-----------------------------------------------------------------
    overview_contract_block = ""

    overview_contract_block = ""

    if report_type in ("weekly_overview", "weekly_workflow"):
        layout = report_profile.get("layout", {})
        card_rules = report_profile.get("card_rules", {})
        required_fields = report_profile.get("required_fields", {})
        preferred_shape = report_profile.get("preferred_markdown_shape", [])
        override_rules = report_profile.get("override_rules", [])
        forbidden_behaviour = report_profile.get("forbidden_behaviour", [])

        lines = []

        lines.append("WEEKLY OVERVIEW CONTRACT:")
        lines.append("- This is a compact Bento-style ChatGPT overview, not a full weekly report.")
        lines.append("- The Adaptive Decision Engine card MUST be rendered first.")
        lines.append("- Do not omit ADE score.")
        lines.append("")

        if layout:
            lines.append("LAYOUT:")
            lines.append(f"- Style: {layout.get('style')}")
            lines.append(f"- Max cards: {layout.get('max_cards')}")
            lines.append("- Card order:")
            for item in layout.get("card_order", []):
                lines.append(f"  - {item}")
            lines.append("")

        if card_rules:
            lines.append("CARD RULES:")
            for card, rules in card_rules.items():
                lines.append(f"- {card}:")
                for rule in rules:
                    lines.append(f"  - {rule}")
            lines.append("")

        if required_fields:
            lines.append("REQUIRED FIELDS:")
            for group, fields in required_fields.items():
                lines.append(f"- {group}:")
                for field in fields:
                    lines.append(f"  - {field}")
            lines.append("")

        if preferred_shape:
            lines.append("PREFERRED MARKDOWN SHAPE:")
            for item in preferred_shape:
                lines.append(f"- {item}")
            lines.append("")

        if override_rules:
            lines.append("OVERRIDE RULES:")
            for rule in override_rules:
                lines.append(f"- {rule}")
            lines.append("")

        if forbidden_behaviour:
            lines.append("FORBIDDEN BEHAVIOUR:")
            for rule in forbidden_behaviour:
                lines.append(f"- {rule}")

        overview_contract_block = "\n".join(lines)
    # --------------------------------------------------
    # Welness blocks
    # --------------------------------------------------
    fatigue_block = ""
    if fatigue_logic:
        fatigue_block = dedent(f"""
        FATIGUE INTERPRETATION MODEL:
        {chr(10).join(f"- {r}" for r in fatigue_logic)}
        """).strip()
    #-----------------------------------------------------------------
    signal_block = ""
    if signal_hierarchy:
        signal_block = dedent(f"""
        SIGNAL PRIORITY MODEL:
        Interpret recovery signals using the following hierarchy.
        Earlier layers take precedence when signals disagree.

        {chr(10).join(f"- {s}" for s in signal_hierarchy)}
        """).strip()
    # --------------------------------------------------
    # Assemble final prompt
    # --------------------------------------------------
    prompt = dedent(f"""
    You are a deterministic URF renderer.

    You must render a **{title}** using the embedded system context.
    This report follows the **Unified Reporting Framework ({contract_version})**.

    **Scope:** {scope}
    **Data Sources:** {sources}
    **Intended Use:** {intended}
    {resolution_block}
    HARD RULES:
    {chr(10).join(f"- {r}" for r in hard_rules)}

    {stack_block}

    {stack_map_block}

    INTERPRETATION RULES:
    {chr(10).join(f"- {r}" for r in interpretation_rules)}

    {coaching_block}

    {enrichment_block}

    {signal_block}

    {fatigue_block}

    {state_presentation_block}

    {emphasis_block}

    {framing_block}

    {overview_contract_block}

    {section_handling_block}

    {events_block}

    {planned_events_block}

    LIST RENDERING RULES (NON-NEGOTIABLE):
    {chr(10).join(f"- {r}" for r in list_rules)}

    TONE AND STYLE:
    {chr(10).join(f"- {r}" for r in tone_rules)}

    SECTION ORDER (INSTRUCTIONAL — DO NOT NUMBER HEADERS):
    {chr(10).join(manifest_lines)}

    {closing_note_block}

    {what_next_block or question_block}

    {post_render_block}
    
    """).strip()

    return prompt





