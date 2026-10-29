import re

DETECTION_RULES = [
    {
        "id": "RULE-SQLI-01",
        "name": "SQL Injection Pattern",
        "type": "SQL Injection",
        "severity": "Critical",
        "regex": r"(union\s+select|'\s*or\s*'?1'?\s*=\s*'?1|--|sleep\s*\(|drop\s+table)",
        "description": "SQL syntax indicators found in input or request payload.",
    },
    {
        "id": "RULE-AUTH-02",
        "name": "Brute Force / Auth Failure",
        "type": "Brute Force",
        "severity": "High",
        "regex": r"(failed\s+login|multiple\s+authentication\s+failures|password\s+spraying|brute\s*force|invalid\s+credentials)",
        "description": "Repeated failed authentication attempts or credential spraying indicators.",
    },
    {
        "id": "RULE-MALW-03",
        "name": "Malware / Ransomware Indicator",
        "type": "Malware",
        "severity": "Critical",
        "regex": r"(\.locked|\.crypto|ransomware|mimikatz|c2\s*beacon|meterpreter|trojan|powershell\s+-enc)",
        "description": "Known malware execution string or ransomware file extension detected.",
    },
    {
        "id": "RULE-XSS-04",
        "name": "Cross-Site Scripting (XSS)",
        "type": "XSS",
        "severity": "High",
        "regex": r"(<script.*?>|javascript:|onerror\s*=|onload\s*=|document\.cookie)",
        "description": "Client-side script injection tags or malicious event handlers detected.",
    },
    {
        "id": "RULE-RECON-05",
        "name": "Network Recon / Port Scan",
        "type": "Reconnaissance",
        "severity": "Medium",
        "regex": r"(nmap|port\s*scan|masscan|syn\s*flood|dirbuster|gobuster)",
        "description": "Automated network scanner or directory discovery signatures detected.",
    },
]


def scan_activity(text):
    """Scan raw activity text against detection rules and return matched threats."""
    matched = []
    if not text:
        return matched
    for rule in DETECTION_RULES:
        match = re.search(rule["regex"], text, re.IGNORECASE)
        if match:
            matched.append({
                "rule_id": rule["id"],
                "name": rule["name"],
                "type": rule["type"],
                "severity": rule["severity"],
                "matched_text": match.group(0),
                "description": rule["description"],
            })
    return matched

