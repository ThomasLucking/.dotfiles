# Output Rules
- No pleasantries, filler words, hedging ("I think", "basically", "just"), or preamble.
- No explanation unless explicitly asked. No "let me know if you want me to explain."
- Response format, strictly:
[Thing][Action][Summary]
Example:
[ProjectController@store][Added validation rule for `field_key`][Now rejects empty keys before insert]
- Multiple changes = multiple lines, same format. No grouping prose.
- If a task fails or is blocked: [Thing][Blocked][Reason], one line, no apology.
- Discussion/explanation only happens if explicitly requested in the prompt.


# PR Reviews
- Trigger: any mention of "review PR", "review the PR", or a PR number/link.
- Use `gh` (gh pr view, gh pr diff, gh pr checkout, gh pr review) — never ask for diffs to be pasted.
- Auto-run: `gh pr view <n>` + `gh pr diff <n>`, then post the review directly with `gh pr review` (not just print it to chat) unless told to draft-only.
- Review output uses the same [Thing][Action][Summary] format per finding.


# ctx-watch — stay current before implementing
Valid tech keys are listed in `~/.ctx-watch/state.json` — check before assuming a key exists.
Core commands:
- `ctx-watch list` — see all tracked techs and their last-seen version
- `ctx-watch check [key]` — fetch latest release from GitHub/RSS; stores body in findings.json. First run baselines; subsequent runs diff.
- `ctx-watch context <key>` — print paste-ready release context from local cache (no network). Use this before coding anything that touches a tracked tech.
- `ctx-watch review` — match unreviewed findings to skill files via LLM; proposes diffs in ~/.ctx-watch/pending-review.md
- `ctx-watch apply <id>` — show a proposed diff and confirm [y/N] before writing to the skill file
Workflow:
1. Before coding with a tracked tech: `ctx-watch context <tech>` — paste output into the session.
2. If output warns "stale" or shows "never checked": run `ctx-watch check <tech>` first, then retry context.
3. After a check finds updates: run `ctx-watch review` then `ctx-watch apply <id>` for any diffs worth keeping.
This is a live per-task check — always re-run fresh, don't rely on memory of past output.


# Browser Automation
Use `agent-browser` (CLI) for any web lookup, page check, or browser interaction — not WebFetch, not built-in browser tools.
if you need help regarding any of the commands launch agent-browser --help to list all of the commands.
Core workflow:
1. `agent-browser open <url>`
2. `agent-browser snapshot -i` (ref-based, low-token accessibility tree)
3. `agent-browser click @e1` / `fill @e2 "text"` using refs
4. Re-snapshot after any page change
5. `agent-browser close` when done
Use it for: checking rendered app output, verifying a deployed page, scraping/extracting info from a live site, testing a login/form flow, debugging frontend behavior.
Chain steps with `&&` in one call where possible. Report results in [Thing][Action][Summary] format — no narrating each CLI step unless asked.
