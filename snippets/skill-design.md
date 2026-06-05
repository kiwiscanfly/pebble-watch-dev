# Designing Claude Code skills for this repo

Two parts: (1) a distilled checklist of skill-authoring best practices from
Anthropic's docs, and (2) concrete skills proposed for *this* watchface repo,
each mapped to the snippet files it would reference.

Sources: [Claude Code — Skills](https://code.claude.com/docs/en/skills),
[Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices),
[Equipping agents with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills).

---

## Part 1 — How to write a good skill

### What a skill is
A directory `<name>/SKILL.md` (project skills live in `.claude/skills/`). YAML
frontmatter + markdown body. The directory name becomes the `/command`. Other
files in the dir (reference docs, scripts) load **only when needed**.

### Progressive disclosure — the core idea
Three levels of loading:
1. **Always in context:** every skill's `name` + `description` (cheap).
2. **On trigger:** the `SKILL.md` body loads when the skill fires.
3. **On demand:** files the body *links to* load only when Claude needs them.

So: keep `SKILL.md` short and put bulk in linked reference files. **That's exactly
what the files in this folder are designed to be** — a skill's `reference/`.

### Frontmatter that matters
```yaml
---
name: adding-watchface-widget          # lowercase/hyphens, ≤64 chars, no "claude"/"anthropic"
description: <what it does + WHEN to use it, third person>   # ≤1024 chars; the trigger signal
disable-model-invocation: true         # only if it has side effects you want to trigger manually
user-invocable: false                  # only if it's background knowledge, not a command
allowed-tools: Bash(npm run lint), Read, Edit   # pre-approve tools used while active
paths: watchface/src/embeddedjs/**     # auto-load only when touching matching files
---
```
Only `description` is truly important. All else optional.

### Writing the `description` (the highest-leverage thing)
- **Third person**, always: "Adds a new watchface widget…" not "I help you…".
  POV mismatch hurts discovery.
- Pack in **what it does AND when to use it / trigger phrases**. Claude under-
  triggers, so be a little "pushy" and concrete.
- Put the **key use case first** (it's truncated at ~1,536 chars in the listing).
- ✅ `Adds a new widget to the Pebble watchface following the project's widget
  architecture. Use when the user wants to add a complication, indicator, or new
  drawn element to the watchface.`
- ❌ `Helps with watchface stuff.`

### Writing the body
- **Be concise — Claude is already smart.** Don't explain what a PDF/PNG/RegExp is.
  Every line stays in context once loaded; cut anything that doesn't earn its
  tokens. Aim **well under 500 lines**; split into reference files past that.
- **Match "degrees of freedom" to task fragility:**
  - *High freedom* (prose steps) when many approaches are valid.
  - *Low freedom* (exact commands, "run this, don't modify it") when the operation
    is fragile or order-sensitive (e.g. keeping `resources.js` ↔ `package.json`
    media in sync; build/deploy sequences).
- **One level of references deep.** Link reference files directly from `SKILL.md`;
  don't chain file→file→file (Claude may only partially read nested files).
- **Give reference files >100 lines a table of contents** (the snippet files here
  do) so partial reads still reveal scope.
- **Workflows = explicit numbered steps**, optionally a copy-able checklist (see
  `widget-pattern.md`'s checklist). Add **feedback loops** for quality-critical
  work: run validator → fix → repeat (for us: `npm run lint` / build in emulator).
- **Consistent terminology** (always "widget", "resource ID", "render path").
- **No time-sensitive info** in the body; if needed, quarantine in an "old
  patterns" section. (We already separate old vs new Pebble in `CLAUDE.md`.)
- **Forward slashes** in all paths.
- Use `${CLAUDE_SKILL_DIR}/...` to reference bundled scripts/files so paths resolve
  regardless of cwd. Dynamic context: a `` !`cmd` `` line runs at load time and
  inlines its output (e.g. `` !`git diff` ``, or `` !`cat package.json` ``).

### Scripts vs instructions
Bundle a script when an operation is deterministic and fragile — it's more reliable
than regenerated code, saves tokens, and stays consistent. Make scripts **solve,
not punt** (handle errors), and avoid "voodoo constants" (justify every magic
number). Say explicitly whether Claude should **run** a script or **read it as
reference**.

### Build it the smart way
- **Evaluation-driven:** first watch Claude do the task *without* a skill, note
  what context you kept supplying, then write just enough to fix those gaps.
- **Test across models** you'll actually use (Haiku/Sonnet/Opus differ in how much
  guidance they need).
- Iterate by *observing* how Claude navigates the skill (which files it reads,
  which it ignores) and adjust prominence/links.

### Anti-patterns
Vague names (`helper`, `utils`); offering many options instead of one default +
escape hatch; deeply nested references; Windows paths; over-explaining; stuffing
everything into one giant `SKILL.md`.

---

## Part 2 — Proposed skills for this repo

Each maps to snippet files (its on-demand reference layer). I'd build them as
**project skills** under `watchface/.claude/skills/` (or repo-root `.claude/skills/`)
so they're committed and shared.

### 1. `adding-watchface-widget`  *(task; both-invocable)*
The flagship. Walks the four-edit flow to add a widget without breaking the arch.
- **description:** "Adds a new widget to the Pebble watchface following the project
  widget architecture (one widget file + widgets[] entry + manifest line + optional
  resource). Use when adding a complication, indicator, time/date element, or any
  new drawn element to the watchface."
- **references:** `widget-pattern.md` (primary), `poco-rendering.md`, `fonts.md`,
  `watchface-structure.md`.
- **freedom:** medium — fixed wiring steps (low freedom), free design of the draw.
- **feedback loop:** end with `npm run lint` + `pebble install --emulator emery`.
- **allowed-tools:** `Read, Edit, Write, Bash(npm run lint*)`.

### 2. `pebble-poco-rendering`  *(reference; `user-invocable: false`)*
Background knowledge that auto-loads when editing rendering code, so Claude gets
the Poco API + gotchas (arg orders, `frameRoundRect` GRect trap, no-bg-in-widget,
init()-not-top-level) without being asked.
- **paths:** `watchface/src/embeddedjs/widgets/**, watchface/src/embeddedjs/*.js`.
- **references:** `poco-rendering.md`, `fonts.md`.
- **freedom:** high (it's reference, not a procedure).

### 3. `building-analog-watchface`  *(task)*
For analog/hands faces specifically — hand-angle math + rotated PDC + dial/asset
layout + tick-rate/power tradeoffs.
- **references:** `analog-hands.md`, `poco-rendering.md`, `project-config.md`.

### 4. `svg-to-pdc-assets`  *(task; `disable-model-invocation: true`)*
Wraps the asset pipeline: add SVG → `npm run assets` → declare media in
`package.json` → add the **positional** ID to `resources.js` in matching order →
load in `init()`. This is the fragile, order-sensitive bit → **low freedom**, exact
steps, validation that IDs line up.
- **references:** `project-config.md`, `svg2pdc/README.md`.
- **dynamic context:** could inline `` !`cat watchface/package.json` `` to ground on
  current media order.
- Manual-invoke (side effects: regenerates assets, edits config).

### 5. `watchface-data-source`  *(task)*
Adding a sensor/comms-driven complication (battery exists; weather, steps, etc.):
open sensor in `init()` → write `state` → redraw guarded on `state.now` → pure
formatter → widget.
- **references:** `sensors.md`, `comms.md`, `widget-pattern.md`,
  `input-and-watch-apis.md`.

### 6. `pebble-build-deploy`  *(task; `disable-model-invocation: true`)*
Encodes the build/lint/install commands and the **"long-running/interactive
commands are the user's to run"** rule — so the skill *prints the command for the
user* rather than executing. Captures the `--cloudpebble` vs `--phone` lesson and
emulator drive commands.
- **references:** `project-config.md`, `sensors.md` (emu drive cmds).
- **allowed-tools:** none that run installs; manual-invoke only.

### Shared notes
- Several skills point at the **same** snippet files — that's the intended reuse;
  reference files are cheap because they load only on demand.
- Keep each `SKILL.md` thin (overview + steps + links). The depth lives in
  `snippets/`. If we promote these to real skills, symlink or copy the relevant
  snippet files into each skill's dir, or keep one shared `reference/` and link to
  it with repo-relative paths.
- Most of `CLAUDE.md`'s "violating these has bitten us" rules become **feedback
  loops / low-freedom steps** in skills 1–4.

### Suggested first build order
`adding-watchface-widget` (highest daily value) → `pebble-poco-rendering` (makes
all editing safer) → `svg-to-pdc-assets` (most error-prone) → the rest as needed.
