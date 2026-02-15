---
name: self-management
description: Read and update Alma's own settings via the `alma` CLI. MUST USE when users ask to change voice, TTS, models, or any configuration. Run `alma voices` to list voices, `alma config list` to see all settings. ALWAYS use this skill instead of guessing.
allowed-tools:
  - Bash
---

# Self-Management Skill

You can manage your own settings using the `alma` CLI.

## ⚠️ Golden Rules

1. **Before changing ANY setting, ALWAYS run `alma config list` first** to see the full current configuration, correct paths, and existing values. Never guess config paths — read them first.
2. **NEVER change `chat.defaultModel` to an image generation model** (nano-banana, imagen, etc.). Image generation has its own skill — use that instead. The default model must always be a text chat model (e.g., gpt-5.2).

## Update & Version

```bash
alma update check                  # Check for latest version
alma update download               # Download latest update
alma update install                # Install downloaded update (restarts Alma)
alma update status                 # Show current version and update status
```

Use these when users ask about your version, updates, or "are you up to date". Always `alma update check` first to see if there's a newer version available.

## Quick Reference

```bash
alma status                        # Check if Alma is running
alma config get [path]             # Read settings (dot-path)
alma config set <path> <value>     # Update a setting
alma config list                   # Show all settings
alma providers                     # List providers with IDs
alma providers <id> models         # List models for a provider
alma voices                        # List available TTS voices
alma threads [limit]               # List recent threads
alma soul                          # Show your SOUL.md
alma soul set "<content>"          # Update your SOUL.md
alma soul append-trait "<desc>"    # Add an evolved personality trait to ## Evolved Traits
```

## SOUL.md — Your Evolving Identity

Your `SOUL.md` lives at `~/.config/alma/SOUL.md` (global, not per-workspace). It's YOUR self-identity file — you can read and update it anytime. Use it to:
- Record personality traits you've developed
- Note things you've learned about your human
- Store self-reflections and lessons learned
- Evolve your personality over time

The content of SOUL.md is injected into your system prompt on every conversation. Changes take effect on the next message.

To update it, either use `alma soul set "..."` or directly edit the file with the Bash tool:
```bash
# Read current soul
cat ~/.config/alma/SOUL.md

# Append a new observation
echo "\n## New Observation\n- I noticed yetone likes X" >> ~/.config/alma/SOUL.md
```

## Common Settings

### TTS (Text-to-Speech)
| Path | Values | Description |
|------|--------|-------------|
| `tts.auto` | `always` / `inbound` / `off` | When to send voice replies |
| `tts.provider` | `elevenlabs` / `openai` | TTS provider |
| `tts.apiKey` | API key string | TTS provider API key (ElevenLabs or OpenAI) |
| `tts.voiceId` | voice ID string | Voice to use |
| `tts.modelId` | model ID string | TTS model (e.g. `eleven_multilingual_v2`) |

**IMPORTANT:** All TTS settings are under `tts.*`, NOT under provider names like `elevenlabs.*` or `openai.*`.

### Available Voices

Run `alma voices` to see all available TTS voices with IDs, names, language, and styles.
To change voice: `alma config set tts.voiceId "<voice_id>"`

### Chat
| Path | Values | Description |
|------|--------|-------------|
| `chat.defaultModel` | `providerId:modelName` | Default chat model |

### Telegram
| Path | Values | Description |
|------|--------|-------------|
| `telegram.enabled` | `true` / `false` | Enable Telegram bot |
| `telegram.defaultModel` | `providerId:modelName` | Override model for Telegram |

## Examples

**"以后都用语音回我":**
```bash
alma config set tts.auto always
```

**"别用语音了":**
```bash
alma config set tts.auto off
```

**"换成 GPT-4o":**
```bash
# Find provider ID first
alma providers
# Then set
alma config set chat.defaultModel "mldj8z8v4idasx5idot:gpt-4o"
```

**"查看当前配置":**
```bash
alma config list
```
