# Compliance Log Guide

## Overview
This document provides an overview of compliance logging in the audit process. It explains how compliance logs are generated and tracked both in **Cloud Mode** (via ChatGPT) and **Local Python Mode**.

## Compliance Logging in Cloud (ChatGPT) Mode
In **Cloud Mode**, compliance logging is handled automatically by the ChatGPT environment. Logs are generated as part of the audit process and are used for monitoring data integrity, validation status, and any deviations from the expected metrics.

### Cloud Mode Compliance Flow
1. **run_report()** in `audit_core/report_controller.py` initiates the audit process, which involves running all tiers from Tier-0 to Tier-2.
2. During the process, each function logs its compliance to ensure data consistency, such as:
   - Tier-0 validation of athlete data
   - Tier-1 checks for duplicates and integrity
   - Tier-2 enforcement of rules (e.g., no missing events)
3. These logs are captured and stored in a cloud-based stream for easy review and troubleshooting. Compliance logs are included in the audit output in a structured format (e.g., JSON, Markdown).

## Compliance Logging in Local Execution Mode
In **Local Mode**, compliance logs are written to the local filesystem, allowing developers and operators to track the progress of their audit and check for any issues that may arise during execution.

### Local Mode Compliance Flow
1. **run_audit.py** directly triggers each tier module from Tier-0 to Tier-2.
2. As each tier executes, compliance checks are performed, and logs are generated for:
   - Data completeness
   - Validations
   - Metric calculations
3. The logs are saved as **`compliance.log`** or in other custom log files, depending on the configuration.
   - These logs can be manually reviewed after the audit execution to ensure the system’s integrity.

## Key Differences Between Cloud and Local Compliance Logging
| Feature | Cloud (ChatGPT) | Local (Python) |
|:--|:--|:--|
| Log Location | Cloud-based logs | Local `compliance.log` or custom log files |
| Log Format | Structured JSON/Markdown format | Plain text log entries, possibly JSON |
| Accessibility | Automatic, viewable through ChatGPT interface | Manually retrieved from local filesystem |

## Conclusion
Compliance logging is a critical part of the audit process, ensuring the integrity of the data being processed. Both **Cloud Mode** and **Local Mode** handle this process efficiently but with different logging mechanisms suited to their respective environments.

---
