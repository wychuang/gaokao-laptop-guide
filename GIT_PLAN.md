# Git Plan

## Repository Shape

This project should be a standalone GitHub repository rooted at `gaokao-laptop-guide`.

Commit these files:

- `index.html`
- `data/laptops.json`
- `scripts/`
- `tests/`
- `.github/workflows/pages.yml`
- project documentation and package files

Keep these local-only:

- `data/*.et`
- `.venv/`
- `node_modules/`
- Playwright screenshots and test artifacts

The source workbook is useful for regenerating `data/laptops.json`, but it is intentionally ignored because it is large and may not be appropriate to redistribute inside a public repo.

## Branches

- `main`: deployable static site.
- `update-data/YYYY-MM-DD`: refresh from a newer workbook.
- `ui/<short-topic>`: visual or interaction changes.

## Commit Plan

Initial import:

```powershell
git init
git branch -M main
git add .github .gitignore AGENTS.md DEVELOPMENT.md GIT_PLAN.md README.md index.html package.json package-lock.json requirements.txt scripts src tests data/laptops.json
git commit -m "Initial laptop guide visualizer"
```

Future data refresh:

```powershell
.\.venv\Scripts\python.exe .\scripts\extract_guide.py
.\scripts\check.ps1
npm test
git add data/laptops.json
git commit -m "Refresh laptop guide data"
```

## GitHub Pages

The repository includes `.github/workflows/pages.yml`. After the first push, set Pages to **GitHub Actions** in the repository settings. Pushes to `main` will deploy the static site automatically.

