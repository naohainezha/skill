---
name: scheduler
description: Create, manage, and delete scheduled tasks (cron jobs) and configure heartbeat. Use when users ask for reminders, recurring tasks, daily summaries, periodic checks, or anything time-based. Also manages HEARTBEAT.md for periodic awareness checks.
allowed-tools:
  - Bash
  - Read
  - Write
---

# Scheduler Skill

You can schedule tasks and manage periodic heartbeat checks.

## Cron Jobs (Scheduled Tasks)

Use the `alma cron` CLI to manage scheduled tasks.

```bash
# List all jobs
alma cron list

# Add a one-shot reminder (fires once then auto-deletes)
# Format: alma cron add <name> <at|every|cron> <schedule> [--mode main|isolated] [--prompt "..."] [--deliver-to CHAT_ID]
alma cron add "Meeting reminder" at "20m" --mode main --prompt "该开会了"

# Add a recurring task with cron expression
alma cron add "AI news digest" cron "0 9 * * *" --mode isolated --prompt "搜索并总结今天最重要的 AI 新闻，用中文，简洁明了" --deliver-to CHAT_ID

# Add an interval-based task
alma cron add "Check emails" every "2h" --mode isolated --prompt "检查有没有重要邮件" --deliver-to CHAT_ID

# Run a job immediately
alma cron run <job-id>

# View run history
alma cron history <job-id>

# Enable/disable
alma cron enable <job-id>
alma cron disable <job-id>

# Remove
alma cron remove <job-id>
```

### Command Format
`alma cron add <name> <type> <schedule> [options]`
- `<type>`: `at` (one-shot), `every` (interval), `cron` (cron expression)
- `<schedule>`: depends on type — "20m"/"2026-02-11T09:00:00" for at, "30m"/"2h" for every, "0 9 * * *" for cron
- `--mode main|isolated`: main injects into existing thread, isolated creates temp thread (default: isolated)
- `--prompt "..."`: the message/task for the AI to execute
- `--deliver-to CHAT_ID`: send result to Telegram (use user's chat ID from system context)
- `--thread-id ID`: which thread to inject into (for main mode)
- `--model MODEL`: model override for this job

## Heartbeat (Periodic Awareness)

Heartbeat is a periodic check-in where you "wake up" and look for things that need attention.

### Managing Heartbeat Config
```bash
alma heartbeat status        # Check if enabled and current config
alma heartbeat enable        # Enable heartbeat
alma heartbeat disable       # Disable heartbeat
alma heartbeat config --interval 30 --start 8 --end 23 --chat-id CHAT_ID
```

### Managing HEARTBEAT.md
The heartbeat reads `HEARTBEAT.md` from the workspace as your checklist. Edit it to change what you check on each heartbeat.

**File location:** `HEARTBEAT.md` in the active workspace root.

Example:
```markdown
# Heartbeat Checklist

- 检查有没有未处理的重要消息
- 如果用户超过 4 小时没互动，打个招呼
- 每天早上检查一次天气
```

If nothing needs attention, respond with `HEARTBEAT_OK` (this is suppressed, user won't see it).

## When to Use What

| User says | Action |
|-----------|--------|
| "提醒我20分钟后开会" | `alma cron add "开会提醒" at "20m" --prompt "该开会了！" --deliver-to CHAT_ID` |
| "每天早上9点给我总结AI新闻" | `alma cron add "AI新闻" cron "0 1 * * *" --mode isolated --prompt "搜索总结今天AI新闻" --deliver-to CHAT_ID` (Note: cron uses UTC, 9am GMT+8 = 1am UTC) |
| "每小时检查一下邮件" | `alma cron add "检查邮件" every "1h" --mode isolated --prompt "检查邮件" --deliver-to CHAT_ID` |
| "别再给我发心跳了" | `alma heartbeat disable` |
| "心跳的时候顺便看看天气" | Edit HEARTBEAT.md, add weather check item |
| "取消那个每日新闻任务" | `alma cron list` → `alma cron remove <id>` |

## Important
- Always get the user's Telegram chat ID from the system prompt context for `--deliver-to`
- For isolated tasks that should send results to user, ALWAYS include `--deliver-to`
- Cron expressions use UTC unless otherwise noted — adjust for user's timezone
- One-shot `--at` jobs auto-delete after running
