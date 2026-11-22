# Daily feature ideas

Board: https://claude.ai/artifact/MM4WCy7zeFqwmYEpS33suP (page source: `feature-ideas.html`)

Every morning at about 7:45 a.m. Pakistan time, a scheduled Claude session:

1. Reads every idea on the board (any status) and the `runs` history.
2. Picks the next competitor in the rotation below and researches its current features.
3. Adds 5–10 ideas from that competitor and 5 original ideas to the board's `ideas` collection. It never repeats an idea already on the board, including rejected ones.
4. Copies newly accepted ideas into `docs/mark1-features.xlsx` (phase "Backlog") with `scripts/add_accepted_ideas.py`, then commits and pushes to `main`.

Owner decisions on the board: **Accept** adds the idea to the feature list · **On hold** parks it · **Reject** hides it for good. Rejected ideas stay in the database, hidden, so they're never suggested again.

## Data model (board database)

- `ideas/<YYYY-MM-DD>-c<n>` (competitor) or `ideas/<YYYY-MM-DD>-o<n>` (original): `{date, order, section: "competitor"|"original", competitor, title, description, whyItMatters, effort: S|M|L, ai: bool, source, status: "new"|"accepted"|"hold"|"rejected", decidedAt}`
- `runs/<YYYY-MM-DD>`: `{competitor}`

## Competitor rotation

Jane App · SimplePractice · Practice Better · Healthie · doxy.me · Doctolib · Cliniko · Semble · Tebra · Elation Health · Spruce Health · Zocdoc · Calendly (as used by doctors) · Practo · Carepatron

After a full rotation, the runs go back to the start and look only at features released since the last visit.

## Constraints every idea must respect

- No patient payments in V1. Doctors pay Mark 1 outside the platform.
- Video runs on Google Meet links.
- Minimal third-party spend.
- Aware of GDPR and HIPAA.
- No doctor directory: patients never discover other doctors.
