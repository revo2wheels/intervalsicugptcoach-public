# audit_core/errors.py

class AuditHalt(Exception):
    """Raised when audit chain must halt due to integrity or data issues."""
    pass
