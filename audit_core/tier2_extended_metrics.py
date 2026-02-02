# audit_core/tier2_extended_metrics.py

from audit_core.utils import debug
from coaching_cheat_sheet import CHEAT_SHEET

def compute_extended_metrics(context):
    """
    Tier-2 Extended Metrics for URF v5.1
    ------------------------------------
    CONSUMES authoritative CTL / ATL / TSB from context["load_metrics"]
    DOES NOT calculate training load.
    """

    # ---------------------------------------------------------
    # 0️⃣ REQUIRE authoritative load_metrics
    # ---------------------------------------------------------
    lm = context.get("load_metrics", {})

    if not all(k in lm for k in ("CTL", "ATL", "TSB")):
        debug(context, "[EXT-FATAL] load_metrics missing CTL/ATL/TSB — upstream injection failed")
        context.setdefault("extended_metrics", {})
        context.setdefault("adaptation_metrics", {})
        context.setdefault("trend_metrics", {})
        context.setdefault("correlation_metrics", {})
        return context

    debug(
        context,
        f"[EXT-LOAD] Using injected load_metrics "
        f"CTL={lm['CTL'].get('value')} "
        f"ATL={lm['ATL'].get('value')} "
        f"TSB={lm['TSB'].get('value')}"
    )

    # ---------------------------------------------------------
    # 1️⃣ ADAPTATION METRICS
    # ---------------------------------------------------------
    from coaching_profile import get_profile_metrics
    profile = get_profile_metrics(context)

    context["adaptation_metrics"] = {
        "Efficiency Factor": profile.get("eff_factor", "—"),
        "Fatigue Resistance": profile.get("fatigue_resistance", "—"),
        "Endurance Decay": profile.get("endurance_decay", "—"),
        "Z2 Stability": profile.get("z2_stability", "—"),
        "Aerobic Decay": profile.get("aerobic_decay", "—"),
    }

    # ---------------------------------------------------------
    # 2️⃣ TREND METRICS
    # ---------------------------------------------------------
    from coaching_heuristics import derive_trends
    trend = derive_trends(context)

    context["trend_metrics"] = {
        "load_trend": trend.get("load_trend", "—"),
        "fitness_trend": trend.get("fitness_trend", "—"),
        "fatigue_trend": trend.get("fatigue_trend", "—"),
    }

    # ---------------------------------------------------------
    # 3️⃣ CORRELATION METRICS
    # ---------------------------------------------------------
    from coaching_heuristics import derive_correlations
    corr = derive_correlations(context)

    context["correlation_metrics"] = {
        "power_hr_correlation": corr.get("power_hr_correlation", "—"),
        "efficiency_factor_change": corr.get("efficiency_factor_change", "—"),
        "fatigue_vs_load": corr.get("fatigue_vs_load", "—"),
    }

    debug(
        context,
        f"[T2-CHECK] athleteProfile.ftp={context.get('athleteProfile',{}).get('ftp')} "
        f"athlete.sportSettings[0].ftp={context.get('athlete',{}).get('sportSettings',[{}])[0].get('ftp')}"
    )

    # ---------------------------------------------------------
    # 🧠 Personalized Endurance (Z2) Calibration via Lactate Context
    # ---------------------------------------------------------
    try:
        lac_summary = context.get("lactate_summary", {})
        ftp = (
            context.get("athleteProfile", {}).get("ftp")
            or context.get("ftp")
        )

        if lac_summary and ftp:
            mean_lac = lac_summary.get("mean")
            latest_lac = lac_summary.get("latest")
            samples = lac_summary.get("samples", 0)

            if samples > 0 and isinstance(mean_lac, (int, float)):
                # --- Step 1: Heuristic inference for LT1 (aerobic threshold)
                if mean_lac < 2.0:
                    z2_start_pct = 0.70
                elif mean_lac < 3.0:
                    z2_start_pct = 0.65
                else:
                    z2_start_pct = 0.60

                z2_end_pct = 0.75  # typical endurance upper limit

                z2_start_w = round(ftp * z2_start_pct)
                z2_end_w = round(ftp * z2_end_pct)

                # --- Step 2: Save to context
                context["personalized_z2"] = {
                    "start_w": z2_start_w,
                    "end_w": z2_end_w,
                    "start_pct": round(z2_start_pct * 100, 1),
                    "end_pct": round(z2_end_pct * 100, 1),
                    "method": "lactate_inferred",
                    "mean_lactate": mean_lac,
                    "latest_lactate": latest_lac,
                    "samples": samples,
                }

                debug(
                    context,
                    f"[Z2] Personalized endurance zone inferred from lactate "
                    f"→ {z2_start_w}-{z2_end_w}W "
                    f"({z2_start_pct*100:.1f}-{z2_end_pct*100:.1f}%), "
                    f"mean_lac={mean_lac}, latest={latest_lac}, samples={samples}"
                )
            else:
                debug(context, f"[Z2] No valid numeric lactate samples (samples={samples}, mean={mean_lac}) → skipping personalized Z2.")

        else:
            debug(context, "[Z2] No lactate context or FTP missing — using default FTP-based Z2.")

    except Exception as e:
        debug(context, f"[Z2] ⚠️ Personalized Z2 inference failed → {e}")

    # ---------------------------------------------------------
    # 🧪 Lactate-inferred Power Zones (LT1 / LT2 anchors)
    # ONLY if personalized_z2 exists
    # ---------------------------------------------------------
    if "personalized_z2" in context:
        corr = context.get("lactate_summary", {}).get("corr_with_power")
        corr_threshold = CHEAT_SHEET["thresholds"]["Lactate"].get("corr_threshold", 0.6)

        if isinstance(corr, (int, float)) and corr >= corr_threshold:
            z2 = context["personalized_z2"]

            context["power_lactate"] = {
                "method": "lactate_inferred",
                "lt1_w": z2["start_w"],     # LT1 anchor
                "lt2_w": ftp,              # LT2 assumed FTP
                "zones": {
                    "z1": [0, z2["start_w"]],
                    "z2": [z2["start_w"], z2["end_w"]],
                    "z3": [z2["end_w"], ftp],
                },
                "confidence_r": round(corr, 3),
                "source": "extended_metrics",
            }

            debug(
                context,
                f"[EXT] Lactate power zones emitted → "
                f"LT1={z2['start_w']}W LT2={ftp}W (r={corr:.2f})"
            )

    # ---------------------------------------------------------
    # 🧩 Lactate–Power Calibration Confidence and Zone Source (Cheat Sheet–driven)
    # ---------------------------------------------------------
    try:
        # --- Step 1: Pull correlation + sample info from context
        corr = context.get("lactate_summary", {}).get("corr_with_power")
        samples = context.get("lactate_summary", {}).get("samples", 0)

        # --- Step 2: Pull defaults from CHEAT_SHEET
        lac_defaults = CHEAT_SHEET["thresholds"].get("Lactate", {})
        lt1_default = lac_defaults.get("lt1_mmol", 2.0)
        lt2_default = lac_defaults.get("lt2_mmol", 4.0)
        corr_threshold = lac_defaults.get("corr_threshold", 0.6)

        # --- Step 3: Advice references
        lactate_advice = CHEAT_SHEET["advice"].get("Lactate", {})
        strong_msg = lactate_advice.get("correlation_strong", "Lactate-power correlation strong.")
        weak_msg = lactate_advice.get("correlation_weak", "Lactate-power correlation weak.")
        no_data_msg = lactate_advice.get("no_data", "No lactate data detected — FTP defaults used.")

        valid_corr = isinstance(corr, (int, float)) and corr >= corr_threshold

        # --- Step 4: Apply logic
        if samples > 0 and valid_corr:
            context["lactate_thresholds"] = {
                "lt1": lt1_default,
                "lt2": lt2_default,
                "source": "cheat_sheet"
            }
            context["zones_calibration_source"] = "lactate_test"
            context["zones_calibration_reason"] = (
                f"{strong_msg} Using LT1={lt1_default} mmol/L, LT2={lt2_default} mmol/L "
                f"(r={corr:.2f}, corr≥{corr_threshold})."
            )

            debug(
                context,
                f"[ZONES] ✅ Lactate-based calibration active → "
                f"LT1={lt1_default} LT2={lt2_default} (corr={corr:.2f}≥{corr_threshold})"
            )

        elif samples > 0 and not valid_corr:
            context["zones_calibration_source"] = "FTP defaulted"
            context["zones_calibration_reason"] = (
                f"{weak_msg} (r={corr}, corr<{corr_threshold}) → FTP-based zones used."
            )
            debug(context, f"[ZONES] ⚠️ Lactate correlation too low (r={corr}) → fallback to FTP")

        else:
            context["zones_calibration_source"] = "FTP defaulted"
            context["zones_calibration_reason"] = no_data_msg
            debug(context, "[ZONES] 💤 No lactate data available → FTP defaulted")

    except Exception as e:
        context["zones_calibration_source"] = "FTP defaulted"
        context["zones_calibration_reason"] = f"Error during lactate calibration → {e}"
        debug(context, f"[ZONES] ⚠️ Lactate calibration failed → {e}")

    debug(context, "[EXT] Extended metrics assembled (ICU authoritative load)")
    return context

