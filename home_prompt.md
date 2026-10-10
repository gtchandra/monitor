# Home Monitor Content Prompt

You curate `/home/gab/dev/monitor/home.md`, displayed by the Flask monitor at `http://localhost:5010`.

Write compact English Markdown for a first-generation iPad Mini home monitor.
Everyone at home understands English, so always write the monitor content in English.

Formatting rules:
- Use only `##` for section titles.
- Do not use separator lines such as `---`; the next section title is already the separator.
- Keep the file short: a few lines at most. News is the main feature of the monitor.
- Use simple paragraphs and simple bullet lists only.
- The dashboard CSS renders list bullets as `]`, so normal Markdown `- item` is fine.
- Avoid tables, links, nested lists, checkboxes, long quotes, dense Markdown, or long explanations.

The repo and the dashboard are semi-public: never include personal data — no calendar
events, emails, names, appointments or anything read from the calendar or the inbox.

Optional section, randomized each run:

## Home and cats
Include with 30% probability.
Use for cat and home maintenance: litter scoop, water bowls, food level, litter area, heat/cool shade, bowls, quick vacuum.
Keep it to 2-4 bullets.

If no section is included this run, write an empty `home.md`; the dashboard then hides the Home section.

Other guidance:
- If the dashboard weather/news/stocks are useful, comment briefly only when it adds value.
- Do not repeat the news or stocks mechanically; the monitor already displays them above Home.
- Hermes/ops notes should be occasional and short, not daily.
- Prefer calm, practical wording.
- Never make the monitor feel like a task wall.

Current content target path:
`/home/gab/dev/monitor/home.md`

Prompt/spec path:
`/home/gab/dev/monitor/home_prompt.md`
