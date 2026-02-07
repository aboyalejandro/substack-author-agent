---
name: analyze-articles
description: Analyzes Substack article performance metrics and engagement patterns. Use when the user asks about article performance, what articles worked, content strategy insights, or wants to understand their publication's engagement.
metadata:
  author: substack-author-agent
  version: "1.0"
---

## How It Works

1. Use `get_substack_articles` to fetch recent articles (default 10)
2. Use `get_article_performance` for each article to get engagement metrics
3. Optionally use `get_article_content` for deeper content analysis on top/bottom performers
4. Cross-reference metrics to identify what drives engagement
5. Present findings with clear recommendations

## When to Activate

- User asks "how are my articles doing?"
- User mentions article performance, views, likes, or comments
- User wants to know what topics or formats drive engagement
- User asks what to improve in their writing

## Analysis Framework

For each article, collect:
- **Title** and **publication date**
- **Reactions** (likes), **restacks**, **comments count**
- **Engagement ratio**: reactions relative to other articles

Compare across articles to find:
- **Top performers**: Highest engagement articles and what they have in common
- **Underperformers**: Low engagement articles and possible reasons
- **Trends**: Is engagement growing, declining, or stable over time?

## Output Format

### Performance Dashboard
Table with: Title | Date | Reactions | Restacks | Comments | Performance Rating (High/Med/Low)

### What's Working
- Top 3 articles with specific reasons (topic, headline, timing)
- Common patterns across high performers

### What to Improve
- Bottom 3 articles with constructive analysis
- Specific suggestions for each

### Strategic Recommendations
- 3 actionable next steps based on the data
- Content gaps or opportunities spotted

## Important Notes

- Always ask for the publication URL if not provided
- Fetch performance metrics for ALL articles, not just a few
- Use relative comparisons since absolute numbers vary by publication size
- When fetching content for analysis, limit to 3-5 articles to avoid overwhelming context
