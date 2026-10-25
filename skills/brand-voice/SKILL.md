---
name: brand-voice
description: Extracts and profiles the author's unique writing voice and style from their Substack articles, notes, and comment replies. Use when the user asks to analyze their writing style, extract voice patterns, create a style guide, or wants a reusable prompt template that captures their tone.
metadata:
  author: substack-author-agent
  version: "1.1"
---

## How It Works

1. Use `get_substack_articles` to fetch 5 recent articles
2. Use `get_article_content` for each to get full text
3. Use `get_substack_notes` to fetch 15-20 recent notes for conversational/informal voice
4. Use `get_article_comments` on 1-2 top articles to collect the author's own comment replies (focus on author responses, not reader comments)
5. Analyze voice, tone, structure, and linguistic patterns across all surfaces (articles, notes, and author comment replies)
6. Synthesize findings into a voice profile and style guide
7. Generate a reusable Claude prompt template that captures the author's voice

## When to Activate

- User asks "what's my writing style?"
- User mentions voice analysis, tone extraction, or style guide
- User wants to replicate their voice in AI-generated content
- User asks for a writing prompt template based on their style

## Analysis Framework

Across all surfaces (articles, notes, and comment replies), analyze:

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

**Voice Across Surfaces:**
- How does the author's voice shift between long-form articles and short-form notes?
- In notes: Are they more direct, casual, personal, or opinionated than in articles?
- In comment replies: How do they engage with readers — warmth level, whether they ask questions back, how they handle disagreement or pushback?
- Are there voice elements that appear only in notes/comments but not articles (or vice versa)?

## Output Format

### Voice Profile Summary
2-3 sentence description of the author's voice that captures its essence

### Style Breakdown
- **Tone**: Where they sit on key spectrums (formal-casual, serious-playful, etc.)
- **Structure**: Their typical article architecture
- **Signatures**: Recurring phrases, patterns, or stylistic choices
- **Surfaces**: How their voice adapts across articles (formal register), notes (informal/conversational), and comment replies (interactive/responsive) — and what remains consistent across all three
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
- SURFACE: When writing articles vs. notes vs. replies, adjust [description of how voice shifts]
```

## Important Notes

- Always ask for the publication URL if not provided
- Fetch FULL article content for all 5 articles (need the actual text for voice analysis)
- Focus on what makes this author UNIQUE, not generic writing advice
- The prompt template should be specific enough to produce noticeably different output than default Claude
- When fetching notes, aim for 15-20 to get a representative sample of informal voice
- For comment replies, only analyze messages authored by the publication owner — skip reader comments
