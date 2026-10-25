---
name: homebase
description: Sets up a Claude Code workspace from scratch by interviewing the user (role, goals, recurring tasks, infrastructure, start folder, starter path) and building the global CLAUDE.md, a project folder structure (role, tasks, projects, knowledge, tools), a saved profile and optional git backup and Context Guard. Use on "/homebase", "set up claude code", "claude einrichten", "workspace einrichten", "claude projektordner erstellen", "neues claude setup", or when a user has just installed Claude Code and has no ~/.claude/CLAUDE.md yet.
---

# Claude Homebase: set up your Claude Code workspace

Goal: after 15 minutes the user has one home base for all work with Claude Code. The structure follows one idea:
**role → tasks → projects → knowledge → tools.** Who you are decides what you do repeatedly, that decides how projects
are organised, what Claude should remember and which tools it needs.

Templates live in the `templates/` folder next to this SKILL.md (also at
https://github.com/AntonioBlago/claude-homebase/tree/main/skills/homebase/templates).

## Rules
- Ask ONE question at a time, offer 3 to 5 examples as options, accept free text. Speak the user's language.
- Never overwrite an existing file. If `~/.claude/CLAUDE.md` or a target file exists: show it, propose a merge, write
  only after the user agrees (keep a `.bak` copy).
- Never ask for passwords, API keys or tokens. Only ask WHERE the user keeps them (e.g. a `.env` outside cloud sync).
- Keep the global CLAUDE.md under 200 lines. Only rules that would cause mistakes if missing.
- Nothing is sent, published or installed without a yes.

## Step 1: Interview (save every answer immediately to the profile, see Step 2)

1. **Role:** "What do you do and for whom?" (SEO freelancer for e-commerce, developer, founder, marketing team lead,
   office/backoffice, content creator). Plus language and form of address (du/Sie, informal/formal).
2. **Goals:** "Which 3 results should Claude help you reach in the next 90 days?"
3. **Recurring tasks:** "What do you do every week that follows the same steps?" Collect 3 to 7. Each one becomes a
   skill candidate.
4. **Infrastructure:** operating system; Claude plan (Pro, Max, Team, API); where you work (terminal, VS Code, desktop
   app); Git and GitHub yes/no; cloud sync folder (OneDrive, Dropbox, iCloud); hosting (Railway, Vercel, none);
   tools to connect via MCP (Google Search Console, Notion, Gmail, Visibly AI, none).
5. **Start folder:** "Where should your home base live?" Suggest `~/Claude` or a folder inside the cloud sync. Warn:
   secrets never inside a synced folder.
6. **Starter path:** let the user pick one or more (see table below) and say what each adds.
7. **Brand (optional):** colours, fonts, templates the user already has.

## Step 2: Save the profile
Write `<start folder>/homebase-profile.md` from `templates/homebase-profile.md` and fill it while interviewing. This
file is the single record of all answers; rerunning `/homebase` reads it first and only asks what is missing.

## Step 3: Build the structure
```
~/.claude/                         WHO you are (applies everywhere)
├── CLAUDE.md                      role, rules, style        (templates/global-CLAUDE.md)
├── settings.json                  permissions, hooks         (merge templates/settings.example.json)
├── skills/<task>/SKILL.md         TASKS, one per recurring task
├── learnings/README.md            KNOWLEDGE: rules from mistakes, one file per topic
└── handoffs/                      session handoffs (Context Guard)

<start folder>/                    WHERE you work
├── CLAUDE.md                      map of the folders          (templates/workspace-CLAUDE.md)
├── homebase-profile.md            all interview answers
├── projects/<name>/               PROJECTS, one folder per client or venture
│   ├── CLAUDE.md                  project context             (templates/project/CLAUDE.md)
│   ├── STATUS.md                  status, contacts, decisions (templates/project/STATUS.md)
│   ├── communication/             mails, meeting notes
│   └── YYYY-MM-DD_<task>/         results per task
├── templates/                     offer, report, mail
└── tools/                         TOOLS: scripts that repeat
```
Use folder names in the user's language if they prefer (e.g. `Projekte`, `Vorlagen`, `Werkzeuge`) and write that
choice into the workspace CLAUDE.md.

1. Global CLAUDE.md from the template, filled with role, goals, style, start folder, tools, limits.
2. Create the folders; create one example project from the user's real current work (ask for its name).
3. For the top 1 to 3 recurring tasks: write a short skill each (`~/.claude/skills/<task>/SKILL.md`, frontmatter
   `name` + `description` with trigger words, then steps). Start small, the user improves them over time.
4. `learnings/README.md` from the template.
5. Settings: merge `templates/settings.example.json` into `~/.claude/settings.json` (keep existing keys).

## Step 4: Starter path
| Path | Adds | Link |
|---|---|---|
| SEO | client workflow status quo, potential, offer, PDF; SEO data via MCP | https://github.com/AntonioBlago/claude-code-seo-starter , https://github.com/AntonioBlago/visiblyai-mcp-server |
| Developer | guardrails, production pitfalls, context control, skill linting | https://www.antonioblago.com/de/skills/vibe-coding/ , https://github.com/AntonioBlago/claude-context-guard , https://github.com/AntonioBlago/delegate-audit |
| Content | blog and podcast repurposing, CMS publishing | https://github.com/AntonioBlago/content-automation , https://github.com/AntonioBlago/anycms , https://github.com/AntonioBlago/visibly-ai-cms-connector |
| AI visibility | brand visibility in ChatGPT, Perplexity, Gemini | https://github.com/AntonioBlago/peec-ai-skills , https://github.com/AntonioBlago/llm-visibility-framework |
| Long-term memory | structured memory across sessions and tools | https://github.com/AntonioBlago/skillmind |

Explain what the chosen path installs, then install only after a yes (clone into the start folder or copy skills).

## Step 5: Optional, ask each
- **Git backup:** `git init` in the start folder with a `.gitignore` that excludes `.env`, `*.key`, `communication/`.
- **Context Guard:** warns when the context gets large and carries a handoff briefing across `/clear`
  (https://github.com/AntonioBlago/claude-context-guard). Follow its README.

## Step 6: Check and hand over
List what was created (tree), show the global CLAUDE.md line count (< 200), then give the user three first prompts:
1. "Read projects/<name>/STATUS.md and tell me the next step."
2. "/<first skill>" on a real task.
3. "Add what you just learned to learnings/<topic>.md."
