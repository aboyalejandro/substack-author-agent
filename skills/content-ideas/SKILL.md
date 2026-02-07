---
name: content-ideas
description: Generates data-driven content ideas for Substack articles and notes. Use when the user asks what to write next, needs topic ideas, content inspiration, or wants to plan their content calendar.
metadata:
  author: substack-author-agent
  version: "1.0"
---

## How It Works

1. Use `get_substack_articles` to fetch recent articles (10-15)
2. Use `get_article_performance` for each to identify top-performing topics
3. Use `get_substack_notes` to fetch recent notes (20+) for engagement signals
4. Cross-reference article topics, note engagement, and gaps in coverage
5. Generate specific content ideas backed by performance data

## When to Activate

- User asks "what should I write about?"
- User mentions content planning, topic ideas, or editorial calendar
- User wants inspiration for their next article or notes
- User asks about content gaps or opportunities

## Ideation Framework

Analyze three data sources:

**From Articles:**
- Which topics got the highest engagement?
- What topics haven't been covered recently?
- Are there popular articles that deserve a follow-up or deeper dive?

**From Notes:**
- What note topics sparked the most reactions/restacks?
- What questions did readers ask in responses?
- What short-form content could become long-form articles?

**From Gaps:**
- Topics the author covers but hasn't written about recently
- Trending topics in the author's niche (based on what performed well)
- Reader requests or unanswered questions from comments

## Output Format

### 3 Article Ideas
For each:
- **Headline**: A compelling, specific title
- **Angle**: What makes this take unique or timely
- **Evidence**: Which data point (top article, popular note, gap) inspired this
- **Format suggestion**: Listicle, deep-dive, how-to, opinion, case study

### 5 Note Ideas
For each:
- **Opening hook**: The first 1-2 sentences
- **Format**: Short take, thread, question, hot take, personal story
- **Why it should work**: Based on what formats/topics performed best

### Content Calendar Suggestion
- Recommended posting rhythm based on current frequency
- Which ideas to prioritize first and why

## Important Notes

- Always ask for the publication URL if not provided
- Base ALL suggestions on actual performance data, not generic advice
- Be specific with headlines - "7 Lessons from Building X" not "Write about your experience"
- Consider the author's voice and existing content themes
