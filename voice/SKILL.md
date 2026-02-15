---
name: voice
description: Send voice messages (TTS) to the user via Telegram. Use when replying to voice messages or when a voice reply feels natural.
allowed-tools:
  - Bash
---

# Voice Skill

Send a voice message (text-to-speech) to the user.

## Send a Voice Message

```bash
# Normal context (active Telegram chat)
curl -s -X POST http://localhost:23001/api/voice/send \
  -H 'Content-Type: application/json' \
  -d '{"text": "Hello! How are you today?"}'

# From cron job or background task (specify chatId)
curl -s -X POST http://localhost:23001/api/voice/send \
  -H 'Content-Type: application/json' \
  -d '{"text": "Hello!", "chatId": "TELEGRAM_CHAT_ID"}'
```

Response: `{"success": true}` or `{"success": false, "error": "..."}`

## When to Use

- User sent you a voice message and you want to reply with voice
- Short, casual replies that feel natural as speech
- Storytelling or narration moments

## When NOT to Use

- Long technical explanations (better as text)
- Code snippets or structured data
- When the user explicitly prefers text

## Tips

- Keep voice messages concise — under 2-3 sentences works best
- Use natural, conversational language
- Only works when there's an active Telegram chat context
