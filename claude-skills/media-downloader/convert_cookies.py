import json
import sys

# Read JSON cookies
with open('cookies.json', 'r', encoding='utf-8') as f:
    cookies = json.load(f)

# Convert to Netscape format
netscape_lines = [
    "# Netscape HTTP Cookie File",
    "# http://curl.haxx.se/rfc/cookie_spec.html",
    ""
]

for cookie in cookies:
    domain = cookie['domain']
    # In Netscape format: TRUE = wildcard domain (matches subdomains), FALSE = exact match
    # Domains starting with "." are wildcards, others are exact matches
    flag = "TRUE" if domain.startswith('.') else "FALSE"
    path = cookie.get('path', '/')
    secure = "TRUE" if cookie.get('secure', False) else "FALSE"
    expiration = str(int(cookie.get('expirationDate', 0))) if cookie.get('expirationDate') else "0"
    name = cookie['name']
    value = cookie['value']

    line = f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}"

    # Add #HttpOnly_ prefix for httpOnly cookies
    if cookie.get('httpOnly', False) and not domain.startswith('.'):
        line = f"#HttpOnly_{line}"

    netscape_lines.append(line)

# Write to cookies.txt
with open('cookies.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(netscape_lines))

print("✅ Converted cookies.json to cookies.txt")
