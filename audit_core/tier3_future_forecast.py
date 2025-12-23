"""
tier3_future_forecast.py
------------------------

Unified Reporting Framework (URF v5.1+)
Tier-3: Future Forecast Module

Purpose:
- Compute future fitness state (CTL, ATL, TSB projections)
- Generate forward-looking coaching actions
- Merge planned Intervals.icu workouts into predictive load model

Inputs:
  - semantic (Tier-2 canonical JSON or dict)
  - planned_workouts (list of dicts with date, tss, title, etc.)

Outputs:
  - future_state (dict)
  - actions_future (list of recommendations)

Notes:
- This module is **non-canonical** (forecasting only).
- No Tier-0 → Tier-2 logic may be overridden.
- Forecast spans default 14 days (configurable).
"""

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
