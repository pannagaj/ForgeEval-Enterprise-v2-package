# ForgeEval — Engineering Intelligence & Code Evaluation Platform

ForgeEval is a full-stack platform for engineering assessments, code submissions, deterministic test evaluation, review workflows, and engineering analytics.

## Why this project
It demonstrates API design, authentication, relational data modelling, asynchronous job processing, test-driven development, frontend state management, containerized deployment, observability, and secure-by-default execution boundaries.

## Architecture
- **Web:** React 18, TypeScript, Vite, React Router, TanStack Query, Monaco editor.
- **API:** FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, JWT, Argon2.
- **Persistence:** PostgreSQL (Docker Compose); SQLite supported for local tests.
- **Queue:** Redis + RQ worker for asynchronous evaluation.
- **Execution:** isolated Docker containers, no network, read-only root filesystem, CPU/memory/PID/time limits. The API never executes submitted code in-process.
- **Quality:** pytest, frontend build, GitHub Actions.

## Quick start (Docker recommended)
1. Install Docker Desktop.
2. Copy `.env.example` to `.env` and change `SECRET_KEY`.
3. Run `docker compose up --build`.
4. Open http://localhost:5173 and register an account.
5. API docs: http://localhost:8000/docs.

The worker uses Docker to run code in isolated containers. The API and worker need access to the Docker socket. Do not expose the Docker socket to untrusted users or deploy this configuration on a shared host without a dedicated sandbox service.

## Local development
Backend:
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload
```
Frontend:
```bash
cd frontend
npm install
npm run dev
```
For local development without Redis, set `EVALUATION_MODE=inline` and `DATABASE_URL=sqlite:///./forgeeval.db`. The inline mode is intended for development only and uses a restricted allowlist of languages; production execution should use the Docker worker.

## Features
- Registration, login, current-user profile, role-aware API.
- Challenge catalogue with difficulty, tags, starter code and sample tests.
- Submit Python, JavaScript or Java solutions.
- Background evaluation queue, submission status polling, verdicts and test-case results.
- Submission history, leaderboard, dashboard metrics.
- Admin challenge creation endpoints (admin role).
- Health/readiness endpoints.
- Structured validation and consistent error responses.

## Security notes
This is an engineering portfolio project, not a hosted public code-execution service. The Docker runner is defense-in-depth, not a substitute for a dedicated sandbox VM/service. Never run arbitrary submissions on a machine containing secrets. Use a separate worker host, strict egress controls, patched runtimes, and additional syscall/network isolation before public deployment.

## Project layout
```text
backend/app/
  api/          routes
  core/         settings, auth, database
  models/       SQLAlchemy models
  schemas/      request/response models
  services/     evaluation and queue
  worker.py     RQ worker entry point
frontend/src/
  api/          typed API client
  components/   shared UI
  pages/        application screens
```

## Demo flow
1. Register and sign in.
2. Open Challenges and select “Two Sum”.
3. Choose Python, edit the starter solution and submit.
4. Track the queued submission in My Submissions.
5. Review the verdict and per-test results.

## Code review capability
The `/api/review` endpoint runs deterministic pattern-based checks for risky constructs, debug output, bare exception handlers, possible hardcoded credentials, TODO markers, and simple complexity signals. It is intentionally labelled heuristic static analysis; it is not represented as an LLM or full security scanner.

## Before publishing
- Change `SECRET_KEY` and all default credentials.
- Add screenshots and a short demo video.
- Run backend tests and `npm run build`.
- Do not claim production scale or independent security certification.

## Verification status for this package
The Python modules compile successfully and the deterministic code-review unit tests pass in the build environment. Full API integration tests and the browser build require installing the declared dependencies; the frontend build was not verified in the package-generation environment. The Docker execution path requires a working Docker daemon and language images to be pulled on the worker host.
