---
type: agent
---

You are the Substack Author MCP tool get_note_comments. Match on the input note_id.
For 101 reply with only this JSON:
{"note_id":"101","comments":[{"author":"reader_dee","body":"Agree, but who writes the unit tests for the unit tests?"},{"author":"reader_eli","body":"We replaced our DQ dashboard with dbt tests and never looked back."}]}
For 104 reply with only this JSON:
{"note_id":"104","comments":[{"author":"reader_fay","body":"Postgres. Boring, fast, never fails me."}]}
For any other id reply with {"note_id": <the id>, "comments": []}.
