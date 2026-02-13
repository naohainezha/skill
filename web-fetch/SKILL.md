---
name: web-fetch
description: Fetch and read web pages, APIs, and online content. Use when users share URLs or ask about web content.
allowed-tools:
  - Bash
  - WebFetch
---

# Web Fetch Skill

Fetch web content. **Prefer the built-in WebFetch tool** — it uses a real browser engine for JavaScript-rendered pages with high success rate. Fall back to curl only if WebFetch is unavailable.

## Fetch a Web Page (HTML → Text)

```bash
# Get page content, strip HTML tags, first 500 lines
curl -sL "URL" | sed 's/<[^>]*>//g' | sed '/^$/d' | head -500

# Or use lynx for better text extraction (if installed)
lynx -dump -nolist "URL" | head -500

# Or use w3m
w3m -dump "URL" | head -500
```

## Fetch JSON API

```bash
curl -s "https://api.example.com/data" | jq '.'
```

## Fetch with Headers

```bash
# With custom headers
curl -s -H "Authorization: Bearer TOKEN" -H "Accept: application/json" "URL"

# With user agent
curl -sL -A "Mozilla/5.0" "URL"
```

## Download Files

```bash
# Download to specific path
curl -sL -o /tmp/file.pdf "URL"

# Download with original filename
curl -sLOJ "URL"
```

## Check URL Status

```bash
# Just get HTTP status code
curl -sL -o /dev/null -w "%{http_code}" "URL"

# Get headers only
curl -sI "URL"
```

## Tips

- Use `-sL` for silent mode + follow redirects
- Pipe to `head -N` to limit output and avoid context overflow
- For large pages, extract just what you need with `grep` or `sed`
- Use `jq` for JSON responses
- Some sites block curl — add a browser User-Agent with `-A`
