---
name: yt-search
description: Search YouTube for top trending videos on any topic. Returns structured results sorted by popularity.
allowed-tools: Bash(python *)
---

# YouTube Search

General-purpose YouTube search tool. Finds the top trending videos on whatever topic the user specifies, filtered to the last 3 months and sorted by view count (most popular first).

## Instructions

1. Take the user's search topic from `$ARGUMENTS`
2. Run the script from the repo root:

```
python .claude/skills/yt-search/yt_search.py $ARGUMENTS
```

3. Parse the JSON output and present results as a numbered markdown table:

| # | Title | Channel | Views | Duration | Date | Link |
|---|-------|---------|-------|----------|------|------|

4. After the table, print the total result count and the date range covered.
5. If no results found, say so and suggest the user try a broader topic.

## Output rules

- Do NOT truncate titles — show them in full
- Keep the table clean and scannable
- The results are already sorted by views (highest first) — preserve that order
- Every row must include a clickable `[Watch](url)` link
