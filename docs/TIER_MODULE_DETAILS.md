# Tier-by-Tier Module Details — v16.1

## Tier-0
- `tier0_pre_audit.py` → Fetch activities, wellness, athlete profile, initialize audit state

## Tier-1
- `tier1_controller.py` → Dataset integrity, duplicate detection, total time variance

## Tier-2
- Step-1: `tier2_data_integrity.py` → API count, discipline gaps
- Step-2: `tier2_event_completeness.py` → Validate events, daily summary
- Step-3: `tier2_enforce_event_only_totals.py` → Compute event-only totals
- Step-4: `tier2_calc_integrity.py` → Check Σ(moving_time, TSS, distance)
- Step-5: `tier2_wellness_validation.py` → Align wellness
- Step-6: `tier2_derived_metrics.py` → Compute all derived markers
- Step-7: `tier2_actions.py` → Generate coaching actions
- Step-8: `tier2_render_validator.py` → Validate report output
