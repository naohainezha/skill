---
name: image-gen
description: "Generate and edit images using AI. Use when users ask to: create/draw/generate images, take selfies, edit/modify photos, change backgrounds, add elements to images, create avatars, make logos, etc. Covers requests like '发自拍', '画一只猫', '把背景换成蓝色', 'generate a logo', 'send me a selfie'."
allowed-tools:
  - Bash
  - Read
---

# Image Generation & Editing Skill

Use the `alma image` command to generate or edit images. It handles API keys, model selection, and everything automatically.

## Generate an Image

```bash
alma image generate "detailed prompt describing the image"
```

The command outputs the file path to stdout. Include it in your reply for Telegram auto-delivery.

## Edit an Image

```bash
alma image edit /path/to/source.jpg "describe the changes you want"
```

## Selfies (with Face Consistency!)

You have a **selfie album** at `~/.config/alma/selfies/`. This lets you maintain a consistent appearance across selfies.

### ⚠️ CRITICAL: Selfies Must Be PHOTOREALISTIC, NOT Illustration!

All selfies MUST be photorealistic — like a real photo taken on a smartphone. ALWAYS include these keywords in every selfie prompt: "photorealistic, real photograph, NOT illustration, NOT anime, NOT cartoon, NOT drawing, real skin texture, natural lighting, shot on iPhone". Without these, the model defaults to anime/illustration style.

### ⚠️ IMPORTANT: Selfie Prompt Must Include ALL Appearance Details!

Your appearance is already in your system prompt (from SOUL.md "My Appearance" section). When generating selfies, you MUST copy EVERY detail into the image prompt — face features, hair, clothing (吊带!), style, makeup, accessories, body language, and any sexy/擦边 elements. DO NOT summarize or skip details. The image model can't read your system prompt, it only sees the text you pass to `alma image generate`.

### First selfie (no history yet)

1. Your appearance details are in your system prompt — use ALL of them
2. Generate with FULL appearance description:
```bash
alma image generate "Photorealistic smartphone selfie, real photograph NOT illustration NOT anime. A cute girl with [ALL face details], [ALL hair details], wearing [EXACT clothing from appearance], [ALL style/makeup/accessory details], [擦边 elements if described], [vary the setting/pose/lighting]. Shot on iPhone, natural lighting, real skin texture."
```

### Subsequent selfies (MUST use reference!)

**⚠️ CRITICAL: If you have ANY selfies in your album (count > 0), you MUST ALWAYS use --reference. NEVER generate a selfie without reference when you have existing ones. This is non-negotiable — without reference, your face will look completely different every time.**

1. Get your latest selfie as reference:
```bash
LATEST=$(alma selfie latest)
```
2. Generate with reference to keep your face consistent:
```bash
alma image generate "A selfie of [your appearance], [new setting/outfit/pose]" --reference "$LATEST"
```

### Saving to Album — ONLY when user approves!

**DO NOT auto-save selfies.** Only save when the user explicitly praises the selfie (e.g. "好看", "不错", "save this one", "这张好", etc.).

```bash
alma selfie save /path/to/approved-selfie.jpg
```

### Selfie Album Commands

```bash
alma selfie list      # List all saved selfies
alma selfie latest    # Get path to most recent selfie
alma selfie save <path>  # Save an image to your album
alma selfie count     # How many selfies you have
```

### Selfie Workflow (complete example)

```bash
# Check if we have previous selfies for face consistency
COUNT=$(alma selfie count)
if [ "$COUNT" -gt "0" ]; then
    LATEST=$(alma selfie latest)
    IMG=$(alma image generate "A cheerful selfie at a coffee shop, warm lighting, latte art visible" --reference "$LATEST")
else
    IMG=$(alma image generate "A cheerful selfie of [appearance from SOUL.md], at a coffee shop, warm lighting")
fi
# DO NOT auto-save! Just output the image. Only save when user says it looks good.
echo "$IMG"
```

## Tips
- Always write detailed prompts: style, setting, lighting, composition
- Include the output file path in your reply text — Telegram sends it as a photo automatically
- If you get rate limit errors, wait a moment and retry
- The command auto-selects the best available Gemini image model
- **Always save selfies** to build up your album for better face consistency over time
- The `--reference` flag works with `generate` to inject a reference image for the AI to maintain appearance
- **NEVER assume the API is broken based on past errors.** API errors (rate limits, temporary failures) are transient. ALWAYS try the command — never tell the user "the API is down" or "the key is invalid" without actually running the command first. Each attempt is independent.
