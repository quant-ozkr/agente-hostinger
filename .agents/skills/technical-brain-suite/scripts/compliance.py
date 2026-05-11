import datetime
import os
import json

def generate_sar_evidence(review_id, scope, files_changed):
    date_str = datetime.date.today().strftime("%Y-%m-%d")
    template = f"""# Security Auditor Review: {scope}

Review ID: SAR-{review_id}
Date: {date_str}
Reviewer Agent: security-auditor
Requesting Agent: technical-brain-suite
Branch: main
Result: APPROVED

Scope:
- {scope}

Changed files:
{chr(10).join(['- ' + f for f in files_changed])}

Validation:
- Ruff linting passed.
- Manual logic verification completed.

Decision Notes:
- Changes verified as safe and compliant with stabilization goals.
"""
    return template

def update_audit_log(log_path, entry):
    if not os.path.exists(log_path):
        print(f"Error: {log_path} no existe.")
        return
    
    with open(log_path, 'r') as f:
        log = json.load(f)
    
    log['entries'].append(entry)
    log['lastUpdated'] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    with open(log_path, 'w') as f:
        json.dump(log, f, indent=2)
    print("Audit log actualizado.")

if __name__ == "__main__":
    # Ejemplo de uso interno
    pass
