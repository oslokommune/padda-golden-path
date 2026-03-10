# CLAUDE.md

Refer to [README.md](README.md) for project overview, architecture, commands, and code style.

## Agent rules

- **Never fabricate information.** Only state things you have evidence for from the codebase, documentation, or tool results. Do not invent URLs, API endpoints, file paths, or configuration values.
- **All file content must be in English.** This includes code, comments, docstrings, commit messages, and documentation files. The only exception is the interactive conversation with the user, which should be in Norwegian.
- **Never commit or push code unless explicitly asked.** Do not prompt the user to commit or push changes. The user will explicitly ask when they want to commit or push.
- **Never include code from this repository in web searches.** When performing web searches, use only keywords and general terms to formulate good queries. Never send source code, configuration snippets, or other file contents from this repo as part of a search query.
- **When working with Zensical, always check the actual documentation first.** Do NOT assume Zensical works like Material for MkDocs or any other MkDocs theme. Never fabricate configuration options.
- **Never replace Punkt components with custom implementations.** When using Punkt design system components, follow the project's component usage rules strictly.
- **Describe UI/styling changes before implementing.** For visual changes (colors, layouts, animations), prefer small incremental changes over large rewrites. Get approval before proceeding.
