---
name: analyze-comments
description: Analyzes comment sentiment and audience feedback themes on Substack articles and notes. Use when the user asks about comments, reader feedback, audience sentiment, what readers are saying, or wants to understand audience pain points and desires.
metadata:
  author: substack-author-agent
  version: "1.1"
---

## How It Works

1. If no article or note URL is provided, use `get_substack_articles` to fetch recent articles and identify the most-commented ones as analysis targets
2. Use `get_article_comments` to fetch comments for the selected article(s)
3. For note comment analysis, use `get_substack_notes` to discover recent notes, then use `get_note_comments` for the top 3 notes by recency (the feed does not include per-note engagement counts)
4. Analyze sentiment across all comments — article or note — using the same framework
5. Identify recurring themes, questions, and pain points
6. Surface content opportunities from reader signals
7. Present sentiment breakdown and actionable insights

## When to Activate

- User asks "what are my readers saying?"
- User mentions comments, feedback, or audience sentiment
- User wants to understand reader pain points or desires
- User asks about engagement quality (not just quantity)
- User asks "what are readers saying on my notes?"
- User wants to analyze comment activity across their publication (not just one article)

## Analysis Framework

For each comment, assess:
- **Sentiment**: Positive, negative, neutral, or constructive criticism
- **Type**: Question, praise, disagreement, personal story, request for more, suggestion
- **Theme**: What topic or aspect of the article is the comment about?
- **Engagement depth**: Short reaction vs thoughtful response

Look for patterns:
- **Recurring questions**: What do readers want to know more about?
- **Pain points**: What struggles or frustrations do readers share?
- **Praise signals**: What specific elements do readers love?
- **Content requests**: What are readers explicitly asking for?
- **Cross-surface patterns**: Do readers raise the same themes in note replies as in article comments? This can reveal consistent audience interests or unresolved questions

## Output Format

Output sections apply whether analyzing article comments, note replies, or both. When analyzing both surfaces, note which signals came from articles vs. notes.

### Sentiment Breakdown
- Positive: X% (brief summary of themes)
- Constructive: X% (what readers want improved)
- Neutral: X%
- Negative: X% (if any, with context)

### Top Themes (ranked by frequency)
For each theme: what it is, how many comments mention it, representative quote

### Audience Pain Points & Desires
- What problems are readers trying to solve?
- What content would they value most?

### Content Opportunities
3-5 specific content ideas directly inspired by reader comments, with:
- The reader signal that inspired it
- Suggested angle or format

### Source Breakdown (when analyzing multiple surfaces)
- Article comments: X comments across Y articles — key themes
- Note replies: X replies across Y notes — key themes
- Overlapping signals: topics that appear on both surfaces (highest priority for content planning)

## Important Notes

- Always ask for the publication URL if not provided (article or note URLs also accepted for targeted analysis)
- Use `sort="best_first"` for most engaged article comments
- Include nested replies in the analysis (they often contain the richest feedback)
- For multi-article analysis, use `get_substack_articles` to find the most-commented articles automatically rather than requiring individual URLs
- For note analysis, limit `get_note_comments` to top 3 notes to manage context size
