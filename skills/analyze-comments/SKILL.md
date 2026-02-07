---
name: analyze-comments
description: Analyzes comment sentiment and audience feedback themes on Substack articles. Use when the user asks about comments, reader feedback, audience sentiment, what readers are saying, or wants to understand audience pain points and desires.
metadata:
  author: substack-author-agent
  version: "1.0"
---

## How It Works

1. Use `get_article_comments` to fetch comments for a specific article (or multiple)
2. Analyze sentiment across all comments (positive, negative, neutral, constructive)
3. Identify recurring themes, questions, and pain points
4. Surface content opportunities from reader signals
5. Present sentiment breakdown and actionable insights

## When to Activate

- User asks "what are my readers saying?"
- User mentions comments, feedback, or audience sentiment
- User wants to understand reader pain points or desires
- User asks about engagement quality (not just quantity)

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

## Output Format

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

## Important Notes

- Always ask for the article URL if not provided
- Use `sort="best_first"` for most engaged comments
- Include nested replies in the analysis (they often contain the richest feedback)
- For multi-article analysis, ask which articles to analyze or suggest the most commented ones
