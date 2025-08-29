import re
import time
from collections import defaultdict
from datetime import datetime, timedelta

class AttackDetector:
    def __init__(self):
        self.request_counts = defaultdict(list)
        self.failed_logins = defaultdict(list)
        
        # SQL Injection patterns
        self.sqli_patterns = [
            r"\'.*--",
            r"\".*--",
            r"OR\s+\'1\'=\'1",
            r"OR\s+\"1\"=\"1",
            r"UNION\s+SELECT",
            r"DROP\s+TABLE",
            r"INSERT\s+INTO",
            r"DELETE\s+FROM",
            r"UPDATE\s+.*SET",
            r"EXEC\s*\(",
            r"EXECUTE\s*\(",
            r"sp_executesql",
            r"xp_cmdshell",
            r";\s*DROP",
            r";\s*DELETE",
            r";\s*INSERT",
            r";\s*UPDATE",
            r"WAITFOR\s+DELAY",
            r"BENCHMARK\s*\(",
            r"SLEEP\s*\(",
            r"pg_sleep\s*\(",
            r"EXTRACTVALUE\s*\(",
            r"UPDATEXML\s*\(",
            r"AND\s+\d+=\d+",
            r"OR\s+\d+=\d+",
            r"HAVING\s+\d+=\d+",
            r"ORDER\s+BY\s+\d+",
            r"GROUP\s+BY\s+\d+",
            r"CONCAT\s*\(",
            r"CHAR\s*\(",
            r"ASCII\s*\(",
            r"SUBSTRING\s*\(",
            r"MID\s*\(",
            r"LENGTH\s*\(",
            r"COUNT\s*\(",
            r"LOAD_FILE\s*\(",
            r"INTO\s+OUTFILE",
            r"INTO\s+DUMPFILE"
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r"<script[^>]*>",
            r"</script>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
            r"onmouseover\s*=",
            r"onfocus\s*=",
            r"onblur\s*=",
            r"onchange\s*=",
            r"onsubmit\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<applet[^>]*>",
            r"<meta[^>]*>",
            r"<link[^>]*>",
            r"<style[^>]*>",
            r"expression\s*\(",
            r"url\s*\(",
            r"@import",
            r"<img[^>]*onerror",
            r"<svg[^>]*onload",
            r"<body[^>]*onload",
            r"alert\s*\(",
            r"confirm\s*\(",
            r"prompt\s*\(",
            r"eval\s*\(",
            r"setTimeout\s*\(",
            r"setInterval\s*\(",
            r"document\.cookie",
            r"document\.write",
            r"window\.location",
            r"location\.href",
            r"location\.replace"
        ]
        
        # Command injection patterns
        self.cmd_patterns = [
            r";\s*cat\s+",
            r";\s*ls\s+",
            r";\s*pwd",
            r";\s*id",
            r";\s*whoami",
            r";\s*uname",
            r";\s*ps\s+",
            r";\s*netstat",
            r";\s*ifconfig",
            r";\s*ping\s+",
            r";\s*wget\s+",
            r";\s*curl\s+",
            r";\s*nc\s+",
            r";\s*telnet\s+",
            r";\s*ssh\s+",
            r";\s*ftp\s+",
            r";\s*rm\s+",
            r";\s*mv\s+",
            r";\s*cp\s+",
            r";\s*chmod\s+",
            r";\s*chown\s+",
            r"&&\s*cat\s+",
            r"&&\s*ls\s+",
            r"&&\s*pwd",
            r"&&\s*id",
            r"&&\s*whoami",
            r"\|\s*cat\s+",
            r"\|\s*ls\s+",
            r"\|\s*pwd",
            r"\|\s*id",
            r"\|\s*whoami",
            r"`cat\s+",
            r"`ls\s+",
            r"`pwd`",
            r"`id`",
            r"`whoami`",
            r"\$\(cat\s+",
            r"\$\(ls\s+",
            r"\$\(pwd\)",
            r"\$\(id\)",
            r"\$\(whoami\)"
        ]
        
        # Path traversal patterns
        self.path_patterns = [
            r"\.\.\/",
            r"\.\.\\",
            r"\/etc\/passwd",
            r"\/etc\/shadow",
            r"\/etc\/hosts",
            r"\/proc\/version",
            r"\/proc\/self\/environ",
            r"C:\\windows\\system32",
            r"C:\\boot\.ini",
            r"C:\\windows\\win\.ini",
            r"\.\.\/\.\.\/",
            r"\.\.\\\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e%5c",
            r"..%2f",
            r"..%5c",
            r"%252e%252e%252f",
            r"%252e%252e%255c"
        ]
        
        # Reconnaissance patterns
        self.recon_patterns = [
            r"Nmap",
            r"DirBuster",
            r"Nikto",
            r"sqlmap",
            r"Burp\s+Suite",
            r"OWASP\s+ZAP",
            r"Acunetix",
            r"Nessus",
            r"OpenVAS",
            r"w3af",
            r"Metasploit",
            r"Hydra",
            r"John\s+the\s+Ripper",
            r"Hashcat",
            r"Gobuster",
            r"Dirbuster",
            r"Wfuzz",
            r"Ffuf",
            r"Masscan",
            r"Zmap",
            r"User-Agent.*bot",
            r"User-Agent.*crawler",
            r"User-Agent.*spider",
            r"User-Agent.*scan"
        ]

    def detect_attack(self, payload, ip_address=None, user_agent=None):
        """
        Enhanced attack detection with multiple pattern categories
        """
        attack_types = []
        
        if not payload:
            return False, []
        
        # Check SQL Injection
        if self._check_patterns(payload, self.sqli_patterns):
            attack_types.append("SQL Injection")
        
        # Check XSS
        if self._check_patterns(payload, self.xss_patterns):
            attack_types.append("Cross-Site Scripting (XSS)")
        
        # Check Command Injection
        if self._check_patterns(payload, self.cmd_patterns):
            attack_types.append("Command Injection")
        
        # Check Path Traversal
        if self._check_patterns(payload, self.path_patterns):
            attack_types.append("Path Traversal")
        
        # Check Reconnaissance
        if user_agent and self._check_patterns(user_agent, self.recon_patterns):
            attack_types.append("Reconnaissance Scan")
        
        # Check for brute force attacks
        if ip_address and self._check_brute_force(ip_address):
            attack_types.append("Brute Force Attack")
        
        # Check for DDoS patterns
        if ip_address and self._check_ddos(ip_address):
            attack_types.append("DDoS Attack")
        
        return len(attack_types) > 0, attack_types

    def _check_patterns(self, text, patterns):
        """Check if text matches any of the given patterns"""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _check_brute_force(self, ip_address):
        """Check for brute force attack patterns"""
        now = datetime.now()
        cutoff = now - timedelta(minutes=5)  # 5-minute window
        
        # Clean old entries
        self.failed_logins[ip_address] = [
            timestamp for timestamp in self.failed_logins[ip_address]
            if timestamp > cutoff
        ]
        
        # Add current attempt
        self.failed_logins[ip_address].append(now)
        
        # Check if more than 10 attempts in 5 minutes
        return len(self.failed_logins[ip_address]) > 10

    def _check_ddos(self, ip_address):
        """Check for DDoS attack patterns"""
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)  # 1-minute window
        
        # Clean old entries
        self.request_counts[ip_address] = [
            timestamp for timestamp in self.request_counts[ip_address]
            if timestamp > cutoff
        ]
        
        # Add current request
        self.request_counts[ip_address].append(now)
        
        # Check if more than 100 requests in 1 minute
        return len(self.request_counts[ip_address]) > 100

    def get_attack_severity(self, attack_types):
        """Determine attack severity based on types"""
        severity_map = {
            "SQL Injection": 9,
            "Command Injection": 9,
            "Cross-Site Scripting (XSS)": 7,
            "Path Traversal": 6,
            "Brute Force Attack": 5,
            "DDoS Attack": 8,
            "Reconnaissance Scan": 3
        }
        
        if not attack_types:
            return 0
        
        return max(severity_map.get(attack_type, 1) for attack_type in attack_types)

# Global detector instance
detector = AttackDetector()

def detect_attack(payload, ip_address=None, user_agent=None):
    """Wrapper function for backward compatibility"""
    is_attack, attack_types = detector.detect_attack(payload, ip_address, user_agent)
    return is_attack


