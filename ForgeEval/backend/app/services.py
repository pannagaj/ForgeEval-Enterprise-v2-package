import tempfile, time
from pathlib import Path
from sqlalchemy.orm import Session
from app.models import Submission, Challenge
from app.core.config import settings

IMAGES = {"python": "python:3.12-alpine", "javascript": "node:22-alpine", "java": "eclipse-temurin:21-jdk"}

def _run_docker(language: str, source: str, stdin: str, timeout: int = 5):
    """Execute in a disposable, networkless container. Never run source in the API process."""
    import docker
    client = docker.from_env()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "input.txt").write_text(stdin, encoding="utf-8")
        if language == "python":
            (root / "main.py").write_text(source, encoding="utf-8")
            command = ["sh", "-c", "python /work/main.py < /work/input.txt"]
        elif language == "javascript":
            (root / "main.js").write_text(source, encoding="utf-8")
            command = ["sh", "-c", "node /work/main.js < /work/input.txt"]
        elif language == "java":
            (root / "Main.java").write_text(source, encoding="utf-8")
            command = ["sh", "-c", "javac -d /tmp /work/Main.java && java -cp /tmp Main < /work/input.txt"]
        else:
            raise ValueError("Unsupported language")
        started = time.monotonic()
        container = None
        try:
            container = client.containers.create(
                IMAGES[language], command, network_disabled=True, read_only=True,
                mem_limit="128m", nano_cpus=500_000_000, pids_limit=64,
                user="65534:65534", working_dir="/work",
                volumes={tmp: {"bind": "/work", "mode": "ro"}},
                tmpfs={"/tmp": "rw,noexec,nosuid,size=32m,mode=1777"},
                environment={"PYTHONDONTWRITEBYTECODE": "1"},
                stdout=True, stderr=True
            )
            container.start()
            result = container.wait(timeout=timeout)
            logs_out = container.logs(stdout=True, stderr=False).decode(errors="replace")
            logs_err = container.logs(stdout=False, stderr=True).decode(errors="replace")
            if result.get("StatusCode", 1) != 0 and not logs_err:
                logs_err = f"Process exited with status {result.get('StatusCode')}"
            return logs_out, logs_err, int((time.monotonic()-started)*1000)
        except Exception as exc:
            if container:
                try: container.kill()
                except Exception: pass
            return "", f"Execution failed: {type(exc).__name__}", int((time.monotonic()-started)*1000)
        finally:
            if container:
                try: container.remove(force=True)
                except Exception: pass

def evaluate_submission(db: Session, submission_id: int):
    sub = db.get(Submission, submission_id)
    if not sub: return
    sub.status = "running"; db.commit()
    challenge = db.get(Challenge, sub.challenge_id)
    results = []
    try:
        for index, case in enumerate(challenge.tests):
            stdout, stderr, elapsed = _run_docker(sub.language, sub.source_code, case.get("input", ""))
            actual, expected = stdout.strip(), str(case.get("expected", "")).strip()
            passed = actual == expected and not stderr
            results.append({"case": index + 1, "passed": passed, "expected": expected, "actual": actual[:1000], "stderr": stderr[:1000], "time_ms": elapsed})
    except Exception as exc:
        results.append({"case": 0, "passed": False, "error": f"Execution infrastructure unavailable: {type(exc).__name__}"})
    passed = sum(1 for r in results if r.get("passed"))
    sub.results = results
    sub.score = round(100 * passed / max(len(challenge.tests), 1))
    sub.verdict = "Accepted" if passed == len(challenge.tests) and results else "Wrong Answer"
    sub.status = "completed"
    db.commit()

def enqueue_submission(submission_id: int):
    if settings.evaluation_mode == "inline":
        from app.core.db import SessionLocal
        with SessionLocal() as db: evaluate_submission(db, submission_id)
    else:
        from redis import Redis
        from rq import Queue
        Queue("evaluations", connection=Redis.from_url(settings.redis_url)).enqueue("app.services.run_job", submission_id, job_timeout=90)

def run_job(submission_id: int):
    from app.core.db import SessionLocal
    with SessionLocal() as db: evaluate_submission(db, submission_id)
