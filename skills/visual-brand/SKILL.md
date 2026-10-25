---
name: visual-brand
description: Analyzes Substack cover images (single, bulk, or cross-publication) to extract visual brand DNA and produce image-generation prompts. Use when the user wants to reverse-engineer a cover style, audit brand consistency, or generate a new cover prompt for an article.
metadata:
  author: substack-author-agent
  version: "1.3"
---

## Purpose

Turn Substack covers into image-generation prompts. Output is always ready to paste into any image gen provider (Midjourney, DALL-E, Stable Diffusion, Flux, etc.).

Three modes — pick based on user intent:

---

## Reverse Prompt (analyze existing covers)

Use when: user wants to understand or replicate a cover style, from their own or any other publication. Works for a single article or a full publication — user picks the count.

1. If given article URL(s): call `get_cover_image` for each
2. If given a publication URL: call `get_substack_articles` first (ask user for count, default 5), then `get_cover_image` on each
3. Analyze all fetched covers: palette, subject, layout, mood, style, motifs
4. Output:
   - **Single cover**: bullet analysis + style prompt that reproduces what was seen
   - **Multiple covers**: one-line per cover + outliers flagged + brand template prompt with `[variable]` placeholders for swappable elements

---

## New Cover Prompt (generate for new article)

Use when: user wants a cover prompt for an article they're writing or just published, consistent with their brand.

1. Get article context: title, subtitle, key theme — from user input or `get_article_content` if URL provided
2. Optionally establish brand context first (run Reverse Prompt on their publication, or use one the user already has)
3. Compose a new prompt that: fits the article's topic/mood, follows the brand visual DNA, is ready for image gen
4. If no brand context provided, ask: "Should I analyze your recent covers first to match your style?"

---

## When to Activate

- "Analyze this cover" / "what does this cover look like"
- "Give me a prompt to recreate this style"
- "What's the visual pattern across my publication"
- "Generate a cover prompt for my new article"
- "Take inspiration from [other publication]'s covers"
- "Make a consistent cover prompt based on my brand"

---

## Prompt Structure

Every output prompt must include these fields (omit only if truly absent from source):

- **Subject**: what/who is depicted, pose or action
- **Color palette**: dominant colors, contrast, warm/cool
- **Lighting**: dramatic, soft, neon, natural
- **Layout**: subject position, negative space, framing
- **Style**: photographic, illustrated, 3D render, painterly, graphic design
- **Mood**: professional, playful, bold, minimal, cinematic
- **Format**: `newsletter cover image, portrait 2:3, high resolution`

---

## Output Format

Always tight — no prose paragraphs.

**Single cover:**
1. Image inline
2. Bullet analysis (6–8 bullets max)
3. Prompt in code block

**Bulk / brand template:**
1. All images inline
2. One-line per cover + outliers flagged
3. Brand template prompt in code block (with `[variable]` placeholders for swappable elements)

**New article prompt:**
1. Brand context summary (2–3 bullets) if used
2. Final prompt in code block
3. One line on what was adapted for the article topic
