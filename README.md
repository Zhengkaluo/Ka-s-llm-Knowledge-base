# Markdown Knowledge Base Framework

> An **AI-native** framework for building and maintaining a personal knowledge base out of plain Markdown files. It defines — *as files* — how an AI assistant should help you capture, organize, discuss, and consolidate what you read and think, in a way that is **portable across AI tools** (WorkBuddy, Cursor, Claude Code, Codex, CodeBuddy, or even a plain chat model).

[简体中文](./README.zh-CN.md)

---

## Why this exists

Most "AI + notes" setups break the moment you switch tools, and most people are (rightly) nervous about letting an AI edit their notes freely. This framework solves both:

- **Protocol-as-code.** The AI's behavior contract lives in Markdown files (`SOUL.md`, `SKILL.md`, `AGENTS.md`, `PLATFORMS.md`, `_schema.md`). Any capable AI tool reads them and knows how to behave — no proprietary plugin required.
- **Permission tiers.** Read freely · **preview before any write** · never delete or overwrite. This directly addresses the fear of "the AI silently rewrote my notes."
- **Multi-agent discussion protocol.** A pool of 13 thinking roles (close reader, sociologist, cognitive psychologist, methodology reviewer, moderator…) with a fixed 7-section speaking format and a consolidation step — turning a single model into a structured panel.
- **Cross-platform by design.** A capability matrix and graceful-degradation strategy for 5+ AI tools, so the same protocol runs everywhere.

## What's inside

```
.
├── SOUL.md          # Behavior contract — every AI must read this first
├── SKILL.md         # Full workflows (query / capture / discuss / ingest …)
├── AGENTS.md        # Multi-agent discussion roles & speaking format
├── PLATFORMS.md     # How to run the same protocol across AI tools
├── _schema.md       # Note format spec (frontmatter, naming conventions)
├── _templates/      # 7 note templates (book/podcast/web/video/article/general + overview)
├── tools/           # Optional capability extensions (ebook fetch, OCR, ingest …)
├── _changelog/      # Shared, structured operation log protocol
├── example/         # A fully fictional sample topic so you can see it work
└── scripts/
    └── init-kb.py   # One-command scaffold for an empty knowledge base
```

## Quick start (5 minutes)

1. **Get the framework**
   ```bash
   git clone <this-repo> my-knowledge-base
   cd my-knowledge-base
   ```
2. **Scaffold your empty base**
   ```bash
   python scripts/init-kb.py
   ```
3. **Point your AI at it.** Open the folder in your AI tool of choice and ask it to *"read SOUL.md and run the first-interaction self-check."* It will report the permission rules, the format spec, the loaded workflows, and the current topics — then wait for your command.
4. **Capture your first note.** Paste a screenshot or some text and say "save this to my knowledge base." The AI will infer the source type, propose a topic, and **show you a preview before writing anything**.
5. **(Optional) explore the example**, then delete the `example/` directory when you're ready to make it yours.

## Works with your AI tool

The framework ships with **entry files for all major AI coding/agent tools**, so whichever one you open the folder in, the AI immediately reads the right protocol:

`CLAUDE.md` · `AGENTS.md` (Codex) · `GEMINI.md` · `WARP.md` · `WORKBUDDY.md` · `CODEBUDDY.md` · `.cursorrules` (Cursor) · `.windsurfrules` (Windsurf) · `.github/copilot-instructions.md` (Copilot)

These are thin pointers — they all route to the same core protocol (`SOUL.md`). See [`PLATFORM-ENTRIES.md`](./PLATFORM-ENTRIES.md) for details. Delete the ones you don't use; it won't affect anything.

## Core ideas in one picture

| Layer | File | Answers the question |
|---|---|---|
| Contract | `SOUL.md` | What is the AI allowed to do? |
| Workflows | `SKILL.md` | How does the AI do each task? |
| Roles | `AGENTS.md` | Who speaks in a multi-agent discussion? |
| Portability | `PLATFORMS.md` | How does this run on a different AI tool? |
| Format | `_schema.md` | What does a valid note look like? |

## Design principles

- **The core logic belongs to the knowledge base, not to any single platform.**
- **Platform features only enhance; they are never a hard dependency.**
- **Important rules live in Markdown** — not in some tool's hidden memory.
- **When a tool lacks a capability, degrade explicitly** (see `PLATFORMS.md`).

## Privacy & safety

- The default `.gitignore` **excludes your content** (`topics/` optionally, `_vault/` material, `.config/` credentials, `_changelog/` history) so you don't accidentally publish private notes or secrets.
- Credentials for optional tools go in a local `.env` (see `.env.example`) and are never committed.
- The permission tiers in `SOUL.md` forbid deletion and overwriting by default.

## License

[MIT](./LICENSE) — use it, fork it, build on it. Attribution appreciated but not required.

---

*This framework was extracted and generalized from a personal Markdown knowledge base. The `example/` content is entirely fictional and ships only as a demonstration.*
