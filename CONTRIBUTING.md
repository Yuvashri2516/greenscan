# Contributing to GreenScan+

Thank you for your interest in contributing to GreenScan+. This guide explains how to set up a development environment, follow the project's branch workflow, and submit a pull request.

---

## Development Setup

### 1. Fork and Clone

```powershell
git clone https://github.com/your-username/greenscan.git
cd "greenscan"
```

### 2. Create a Python Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
pip install tensorflow
```

### 3. Install Frontend Dependencies

```powershell
cd frontend
npm install
cd ..
```

### 4. Configure Environment

```powershell
# Backend
Copy-Item backend\.env.example backend\.env

# Frontend
Copy-Item frontend\.env.example frontend\.env
```

Edit `backend/.env` and `frontend/.env` with your local values.

### 5. Start Development Servers

**Terminal 1 — Backend:**
```powershell
.\venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload --port 8001
```

**Terminal 2 — Frontend:**
```powershell
cd frontend
npm run dev
```

---

## Branch Workflow

| Branch | Purpose |
|---|---|
| `main` | Stable, production-ready code |
| `dev` | Active development integration branch |
| `feature/your-feature` | Individual feature branches |
| `fix/your-fix` | Bug fix branches |
| `research/your-topic` | Research experiment branches |

### Recommended Workflow

```powershell
# 1. Start from dev
git checkout dev
git pull origin dev

# 2. Create a feature branch
git checkout -b feature/my-new-feature

# 3. Make changes, then stage and commit
git add .
git commit -m "feat: describe what you changed"

# 4. Push to your fork
git push origin feature/my-new-feature

# 5. Open a pull request into dev
```

---

## Commit Message Convention

Use conventional commit style:

| Prefix | When to use |
|---|---|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation only |
| `refactor:` | Code change without feature/fix |
| `test:` | Adding or updating tests |
| `chore:` | Build tools, config, maintenance |
| `research:` | Research scripts or analysis |

Example: `feat: add multi-language support to chatbot`

---

## Coding Standards

### Python (Backend)
- Follow **PEP 8** style
- Use type hints where practical
- Add docstrings to all public functions
- Do not hardcode secrets — use `config.py` and `.env`
- Do not modify `gsa_engine.py` algorithm without a documented scientific justification

### JavaScript / JSX (Frontend)
- Use functional components with React hooks
- Keep components focused and single-purpose
- Use CSS custom properties from `index.css` design tokens
- Do not add inline styles for colours — use existing CSS variables

### General Rules
- Do not commit `.env` files
- Do not commit `venv/`, `node_modules/`, or `__pycache__/`
- Do not commit `backend/greenscan.db` (runtime data)
- Do not commit binary dataset images

---

## Testing

Before submitting a pull request, verify the following:

### Backend
```powershell
# Health check
curl http://127.0.0.1:8001/health

# Run end-to-end test
.\venv\Scripts\Activate.ps1
python backend/test_e2e.py
```

### Frontend
```powershell
cd frontend
npm run build   # ensure build compiles without errors
```

### Manual Smoke Test
1. Upload a tomato leaf image
2. Verify disease classification returns
3. Verify Grad-CAM heatmap displays
4. Verify Plant Health Score appears
5. Verify recommendations display
6. Verify scan saves to History

---

## Pull Request Expectations

- PR title should clearly describe the change
- Include a short description of what was changed and why
- Do not include unrelated changes in the same PR
- All CI checks must pass before review
- Pull requests to `main` require review and approval
- Research changes require a brief justification in the PR description

---

## Scientific Integrity

GreenScan+ is used in research. Please follow these rules:

- ❌ Do not fabricate test results, accuracy numbers, or validation statistics
- ❌ Do not change the GSA algorithm without documented scientific justification
- ❌ Do not claim expert validation has been completed unless it has
- ✅ Use measured numbers from actual experiments
- ✅ Clearly mark pending validations as PENDING

---

## Reporting Issues

Use the GitHub Issues tab to report:

- Bugs with steps to reproduce
- Feature suggestions (label as `enhancement`)
- Research discrepancies
- Documentation errors

---

## Questions

Open a GitHub Discussion or contact the maintainers through the repository.
