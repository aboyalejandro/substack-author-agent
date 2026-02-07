---
name: analyze-notes
description: Analyzes Substack note performance and engagement patterns. Use when the user asks about note performance, what notes work best, engagement patterns on notes, or wants to understand their note strategy.
metadata:
  author: substack-author-agent
  version: "1.0"
---

## How It Works

1. Use `get_substack_notes` to fetch notes (default 20, paginate with `next_cursor` if needed)
2. Rank notes by reactions + restacks to find top performers
3. Analyze format patterns (length, structure, hooks, CTAs) across top vs bottom performers
4. Identify hot topics and underutilized content patterns
5. Present findings with actionable next steps

## When to Activate

- User asks "how are my notes doing?"
- User mentions note performance, engagement, or reach
- User wants to know what note formats or topics work
- User asks about restacks or reactions on notes

## Analysis Framework

For each note, extract:
- **Reactions** (likes/hearts) and **restacks** (shares)
- **Format**: length (short < 100 words, medium 100-300, long 300+), whether it has images, links, or is text-only
- **Hook quality**: Does the first line grab attention?
- **Topic category**: What subject area does it cover?

## Output Format

### Top 3 Performing Notes
For each: quote the opening line, show reaction + restack counts, explain WHY it worked (format, topic, timing)

### Engagement Pattern Summary
- Best-performing format (short vs long, text vs media)
- Topics that resonate most
- Patterns in top performers vs underperformers

### 5 Content Ideas
Based on what's working, suggest 5 specific note ideas with:
- Suggested opening hook
- Recommended format
- Why it should work (based on data)

## Important Notes

- Always ask the user for their publication URL if not provided
- Use pagination (`next_cursor`) to get enough data for meaningful analysis (aim for 20+ notes)
- If a note has 0 reactions, still include it in the analysis as a learning signal
- Compare relative performance, not absolute numbers
