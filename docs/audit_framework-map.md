# Framework Map

## Overview
This document provides a visual overview of the framework architecture, detailing how the various modules interact within the **IntervalsICU GPT Coach** system. The framework supports both **Cloud Mode** (via ChatGPT) and **Local Python Execution Mode**, and this map outlines how each mode processes the audit chain, from data fetching to report generation.

## Cloud Mode Architecture
In **Cloud Mode**, modules are fetched dynamically from GitHub, and each component communicates over the cloud using APIs and raw data paths. The key components are as follows:

1. **Data Fetching**: 
   - `intervals_icu__jit_plugin` fetches athlete data from external sources (e.g., Strava, TrainingPeaks).
   - Modules such as `audit_core/tier0_pre_audit.py` validate and prepare the data for further auditing.

2. **Audit Chain**:
   - The audit chain is controlled by `run_report()` in `audit_core/report_controller.py`, which internally calls `run_audit()`.
   - Each tier module (Tier-0 to Tier-2) runs sequentially to validate, enforce, and compute audit metrics.

3. **Reporting**:
   - Once the audit is completed, the results are rendered via `render_unified_report.py`, producing a full 10-section Markdown report.

### Cloud Mode Flow Diagram
```plaintext
[Cloud API] → [intervals_icu__jit_plugin] → [audit_core/tier0_pre_audit.py] → [audit_core/tier1_controller.py] → [audit_core/tier2_*] → [render_unified_report.py] → [Unified Report]
