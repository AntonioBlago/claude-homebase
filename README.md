# Claude Homebase: how to set up Claude Code with one structure for everything

A free starter for anyone who just installed Claude Code and asks "where do I put things?". One skill, `/homebase`,
interviews you (role, goals, recurring tasks, infrastructure, start folder, starter path), saves your answers and builds
a Claude Code setup that works for any kind of work, not only code:

**role → tasks → projects → knowledge → tools**

- a global **CLAUDE.md** built from your role (CLAUDE.md template included, kept under 200 lines)
- a **Claude Code project structure** with one folder per client or venture, each with its own CLAUDE.md and STATUS.md
- **skills** for your recurring tasks, **learnings** that turn corrections into rules, optional session handoff
- a `homebase-profile.md` with all your answers, so rerunning `/homebase` only asks what is missing

No dependencies, no network calls, nothing is installed or sent without your yes.

## 1. Install Claude Code (setup in 2 minutes)

Claude Code needs a paid Claude plan (Pro, Max, Team) or an API account. The free claude.ai plan does not include it.

```bash
# macOS, Linux, WSL
curl -fsSL https://claude.ai/install.sh | bash

# Windows PowerShell (no admin needed; Git for Windows is optional)
irm https://claude.ai/install.ps1 | iex
```

Check with `claude --version`, then start `claude` in any folder and log in. Prefer an app? The Claude desktop app and
the VS Code extension include Claude Code. Official guide: [code.claude.com/docs/en/setup](https://code.claude.com/docs/en/setup).

## 2. Add the homebase skill

```bash
git clone https://github.com/AntonioBlago/claude-homebase.git
# macOS / Linux
mkdir -p ~/.claude/skills && cp -r claude-homebase/skills/homebase ~/.claude/skills/
# Windows PowerShell
Copy-Item -Recurse claude-homebase\skills\homebase $env:USERPROFILE\.claude\skills\
```

Restart Claude Code and type `/homebase`.

## 3. The structure it builds

```
~/.claude/                         WHO you are (applies everywhere)
├── CLAUDE.md                      role, rules, style
├── settings.json                  permissions (e.g. .env blocked), hooks
├── skills/<task>/SKILL.md         TASKS: one skill per recurring task
├── learnings/                     KNOWLEDGE: rules from mistakes, one file per topic
└── handoffs/                      session handoffs (with Context Guard)

<your home base>/                  WHERE you work
├── CLAUDE.md                      map of the folders
├── homebase-profile.md            your saved answers
├── projects/<name>/               PROJECTS: CLAUDE.md, STATUS.md, communication/, YYYY-MM-DD_<task>/
├── templates/                     offers, reports, mails
└── tools/                         TOOLS: scripts for anything you do three times
```

Why two levels: Claude Code merges the user CLAUDE.md (`~/.claude/CLAUDE.md`) with the CLAUDE.md of the folder you
start in. Your role and rules load everywhere, project context only where it belongs. Claude Code memory (auto memory)
keeps facts per project on top.

## 4. Pick a starter path

| Path | What you get |
|---|---|
| SEO | [claude-code-seo-starter](https://github.com/AntonioBlago/claude-code-seo-starter): client workflow status quo, potential, offer, PDF; [visiblyai-mcp-server](https://github.com/AntonioBlago/visiblyai-mcp-server): SEO data in Claude via MCP |
| Developer | [claude-context-guard](https://github.com/AntonioBlago/claude-context-guard): context warning and handoff; [delegate-audit](https://github.com/AntonioBlago/delegate-audit): lint skills against DELEGATE-52 rules; [Vibe Coding Set](https://www.antonioblago.com/de/skills/vibe-coding/?utm_source=github&utm_medium=readme&utm_campaign=claude-homebase) (German): 38 production pitfalls as skills |
| Content | [content-automation](https://github.com/AntonioBlago/content-automation), [anycms](https://github.com/AntonioBlago/anycms), [visibly-ai-cms-connector](https://github.com/AntonioBlago/visibly-ai-cms-connector) |
| AI visibility | [peec-ai-skills](https://github.com/AntonioBlago/peec-ai-skills), [llm-visibility-framework](https://github.com/AntonioBlago/llm-visibility-framework) |
| Long-term memory | [skillmind](https://github.com/AntonioBlago/skillmind) |

SEO data for any path: [Visibly AI](https://www.visibly-ai.com/?utm_source=github&utm_medium=readme&utm_campaign=claude-homebase).

## Read more

- [How to set up Claude Code: a guide for beginners](https://www.antonioblago.com/blog/how-to-set-up-claude-code?utm_source=github&utm_medium=readme&utm_campaign=claude-homebase) (German: [Claude Code installieren und einrichten](https://www.antonioblago.com/de/blog/claude-code-installieren-einrichten?utm_source=github&utm_medium=readme&utm_campaign=claude-homebase))
- [Best Claude Code skills for developers (with a 26-billion-token measurement)](https://www.antonioblago.com/blog/best-claude-code-skills-developers?utm_source=github&utm_medium=readme&utm_campaign=claude-homebase)
- [AI hallucinations and the DELEGATE-52 rules](https://www.antonioblago.com/blog/ki-halluzinationen-delegate-52-en?utm_source=github&utm_medium=readme&utm_campaign=claude-homebase)
- [Agentic engineering: 100+ SEO projects solo with AI](https://www.antonioblago.com/blog/agentic-engineering-seo-projects-ai-en?utm_source=github&utm_medium=readme&utm_campaign=claude-homebase)
- [Agentic SEO systems: Claude Code as an SEO control center](https://www.antonioblago.com/blog/agentic-seo-systeme-2026-en?utm_source=github&utm_medium=readme&utm_campaign=claude-homebase)
- [Claude skills in practice: Peec AI MCP case study](https://www.antonioblago.com/blog/claude-skills-peec-ai-mcp-case-study-en?utm_source=github&utm_medium=readme&utm_campaign=claude-homebase)

## Deutsch: Claude Code installieren und einrichten

Claude Homebase ist eine kostenlose Startvorlage, um Claude Code einzurichten. Der Skill `/homebase` fragt deine Rolle,
Ziele, wiederkehrenden Aufgaben, Infrastruktur, deinen Startordner und dein Startpaket ab, speichert die Antworten in
`homebase-profile.md` und baut daraus die globale CLAUDE.md, eine Ordnerstruktur für Projekte, Skills für deine
Aufgaben und eine Learnings-Ablage. Claude Code installieren: unter Windows in PowerShell `irm https://claude.ai/install.ps1 | iex`,
dann den Ordner `skills/homebase` nach `%USERPROFILE%\.claude\skills\` kopieren und `/homebase` eingeben. Claude
antwortet in deiner Sprache, Ordnernamen gibt es auf Wunsch auf Deutsch (Projekte, Vorlagen, Werkzeuge).
Ausführlich: [Claude Code installieren und einrichten](https://www.antonioblago.com/de/blog/claude-code-installieren-einrichten?utm_source=github&utm_medium=readme&utm_campaign=claude-homebase).

## License

MIT, see [LICENSE](LICENSE). By [Antonio Blago](https://www.antonioblago.com/?utm_source=github&utm_medium=readme&utm_campaign=claude-homebase).
