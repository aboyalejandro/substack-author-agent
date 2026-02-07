---
name: brand-voice
description: Extracts and profiles the author's unique writing voice and style from their Substack articles. Use when the user asks to analyze their writing style, extract voice patterns, create a style guide, or wants a reusable prompt template that captures their tone.
metadata:
  author: substack-author-agent
  version: "1.0"
---

## How It Works

1. Use `get_substack_articles` to fetch 5 recent articles
2. Use `get_article_content` for each to get full text
3. Analyze voice, tone, structure, and linguistic patterns across all articles
4. Synthesize findings into a voice profile and style guide
5. Generate a reusable Claude prompt template that captures the author's voice

## When to Activate

- User asks "what's my writing style?"
- User mentions voice analysis, tone extraction, or style guide
- User wants to replicate their voice in AI-generated content
- User asks for a writing prompt template based on their style

## Analysis Framework

Across all 5 articles, analyze:

**Tone & Voice:**
- Formal vs conversational spectrum
- Use of humor, wit, sarcasm
- Emotional register (inspiring, analytical, personal, authoritative)
- First person vs second person vs third person usage

**Structure Patterns:**
- Average paragraph length
- Use of headers, subheaders, bullet points
- Opening patterns (story, question, bold claim, data point)
- Closing patterns (CTA, summary, question, reflection)

**Linguistic Signatures:**
- Favorite phrases or expressions that recur
- Sentence length patterns (short punchy vs flowing)
- Use of metaphors, analogies, examples
- Technical jargon level

**Content Approach:**
- How they introduce topics
- How they support arguments (data, stories, logic, authority)
- How they handle transitions between sections
- Use of personal anecdotes vs external examples

## Output Format

### Voice Profile Summary
2-3 sentence description of the author's voice that captures its essence

### Style Breakdown
- **Tone**: Where they sit on key spectrums (formal-casual, serious-playful, etc.)
- **Structure**: Their typical article architecture
- **Signatures**: Recurring phrases, patterns, or stylistic choices
- **Do's**: Things that define their voice
- **Don'ts**: Things that would feel off-brand

### Reusable Claude Prompt Template
A ready-to-use system prompt that instructs Claude to write in this author's voice:
```
You are writing in the voice of [author]. Their style is characterized by...
When writing as them:
- DO: [specific instructions]
- DON'T: [anti-patterns]
- TONE: [description]
- STRUCTURE: [typical format]
```

## Important Notes

- Always ask for the publication URL if not provided
- Fetch FULL article content for all 5 articles (need the actual text for voice analysis)
- Focus on what makes this author UNIQUE, not generic writing advice
- The prompt template should be specific enough to produce noticeably different output than default Claude
