# XHS Batch Downloader

小红书博主笔记批量下载器。

## CONSTANTS

| Key | Value |
|-----|-------|
| **workdir** | `C:\Users\admin\Projects\xhs-batch-downloader` |
| **entry** | `python cli.py <command>` |
| **output** | `C:\Users\admin\Projects\XHS-Downloader\Volume\Download\` |
| **db** | `C:\Users\admin\Projects\xhs-batch-downloader\data\bloggers.db` |
| **login state** | `C:\Users\admin\Projects\xhs-batch-downloader\browser_data\xhs\` |

> CRITICAL: Entry point is `python cli.py`, NOT `python -m xhs_batch_downloader`.
> All commands below MUST run from workdir.

## QUICK START

```bash
# workdir: C:\Users\admin\Projects\xhs-batch-downloader

# Download 5 notes from a blogger
python cli.py download <BLOGGER_ID> --count 5

# Download all notes from a blogger
python cli.py download <BLOGGER_ID> --all
```

Blogger ID = 24-char hex from profile URL:
`https://www.xiaohongshu.com/user/profile/5c6fb3fb00000000110126a2` -> `5c6fb3fb00000000110126a2`

## ALL COMMANDS

| Command | Usage | Description |
|---------|-------|-------------|
| `download` | `python cli.py download <ID> --count N` | Download N notes from blogger |
| `download` | `python cli.py download <ID> --all` | Download all notes |
| `download` | `python cli.py download <ID> --count N --force` | Force re-download (ignore cache) |
| `download-all` | `python cli.py download-all --count N` | Download from all saved bloggers |
| `add` | `python cli.py add <ID> --alias "name"` | Add blogger to database |
| `list` | `python cli.py list` | List saved bloggers |
| `remove` | `python cli.py remove <ID>` | Remove blogger |
| `alias` | `python cli.py alias <ID> <name>` | Set blogger alias |
| `login` | `python cli.py login` | QR code login (first-time setup) |
| `status` | `python cli.py status` | Check login/system status |

## PIPELINE POSITION

Step 1 of 3:
1. **[THIS] Download** -> output: `C:\Users\admin\Projects\XHS-Downloader\Volume\Download\`
2. Filter (xhs-image-filter) -> input: above path
3. Wash (xhs-comfyui-wash) -> input: filtered output

## TROUBLESHOOTING

| Error | Fix |
|-------|-----|
| `No module named xhs_batch_downloader` | Use `python cli.py`, NOT `python -m` |
| Login failed | Run `python cli.py login`, scan QR within 2 min |
| Signature failed | Re-login: `python cli.py login` |
| API rate limit | Wait and retry, or reduce `--count` |
| UnicodeEncodeError on output | Cosmetic only (Windows GBK encoding), download itself succeeds |
