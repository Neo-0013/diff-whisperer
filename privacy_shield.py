import re

class PrivacyShield:
    """
    Scans and redacts sensitive information from text before it's sent to an LLM.
    """
    
    PATTERNS = {
        "Google API Key": r"AIza[0-9A-Za-z-_]{35}",
        "OpenAI API Key": r"sk-[a-zA-Z0-9]{48}",
        "AWS Access Key": r"AKIA[0-9A-Z]{16}",
        "Generic Secret": r"(?i)\b\w*(password|secret|api_key|token|credential)\w*\b\s*[:=]\s*['\"]([^'\"]+)['\"]",
        "Email Address": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "Internal IP": r"\b(127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3})\b"
    }

    def __init__(self):
        self.findings = []

    def scan(self, text: str):
        """Scans the text for sensitive patterns and populates findings."""
        self.findings = []
        for category, pattern in self.PATTERNS.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                # For generic secrets, we want to redact the value part only
                if category == "Generic Secret":
                    value = match.group(2)
                    start, end = match.start(2), match.end(2)
                else:
                    value = match.group()
                    start, end = match.start(), match.end()
                
                self.findings.append({
                    "category": category,
                    "value": value,
                    "start": start,
                    "end": end
                })
        return self.findings

    def redact(self, text: str):
        """Redacts all found sensitive information from the text."""
        if not self.findings:
            return text
            
        # Sort findings by start position ascending
        sorted_findings = sorted(self.findings, key=lambda x: x['start'])
        
        # Merge overlapping/nested intervals
        merged = []
        for finding in sorted_findings:
            if not merged:
                merged.append({
                    "start": finding["start"],
                    "end": finding["end"]
                })
            else:
                last = merged[-1]
                if finding['start'] <= last['end']:
                    # Overlap or nested
                    last['end'] = max(last['end'], finding['end'])
                else:
                    merged.append({
                        "start": finding["start"],
                        "end": finding["end"]
                    })
                    
        # Redact from right to left (reverse order of merged intervals)
        redacted_text = text
        for interval in reversed(merged):
            redacted_text = redacted_text[:interval['start']] + "[REDACTED]" + redacted_text[interval['end']:]
        
        return redacted_text

    def get_summary(self):
        """Returns a summarized list of found categories."""
        if not self.findings:
            return None
        
        summary = {}
        for f in self.findings:
            cat = f['category']
            summary[cat] = summary.get(cat, 0) + 1
        return summary
