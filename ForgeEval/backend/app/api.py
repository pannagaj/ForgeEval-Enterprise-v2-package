from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.core.db import get_db
from app.core.security import hash_password, verify_password, create_token
from app.dependencies import current_user, admin_user
from app.models import User, Challenge, Submission
from app.schemas import RegisterIn, LoginIn, TokenOut, UserOut, SubmitIn, ChallengeOut
from app.services import enqueue_submission
from app.review import review_code

router = APIRouter(prefix="/api")

@router.post("/auth/register", response_model=TokenOut, status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "An account with this email already exists")
    user = User(name=payload.name, email=email, password_hash=hash_password(payload.password))
    db.add(user); db.commit(); db.refresh(user)
    return {"access_token": create_token(str(user.id)), "user": user}

@router.post("/auth/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Incorrect email or password")
    return {"access_token": create_token(str(user.id)), "user": user}

@router.get("/auth/me", response_model=UserOut)
def me(user: User = Depends(current_user)): return user

@router.get("/challenges", response_model=list[ChallengeOut])
def challenges(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return list(db.scalars(select(Challenge).where(Challenge.active == True).order_by(Challenge.id)))

@router.post("/challenges", response_model=ChallengeOut, status_code=201)
def create_challenge(payload: dict, db: Session = Depends(get_db), user: User = Depends(admin_user)):
    required = {"slug","title","description","difficulty","tests"}
    if not required.issubset(payload): raise HTTPException(422, "Missing required challenge fields")
    item = Challenge(**payload); db.add(item); db.commit(); db.refresh(item); return item

@router.post("/challenges/{challenge_id}/submissions", status_code=202)
def submit(challenge_id: int, payload: SubmitIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    challenge = db.get(Challenge, challenge_id)
    if not challenge or not challenge.active: raise HTTPException(404, "Challenge not found")
    sub = Submission(user_id=user.id, challenge_id=challenge.id, language=payload.language, source_code=payload.source_code)
    db.add(sub); db.commit(); db.refresh(sub)
    try: enqueue_submission(sub.id)
    except Exception:
        sub.status = "failed"; sub.verdict = "Infrastructure Error"; db.commit()
        raise HTTPException(503, "Evaluation queue unavailable")
    return {"id": sub.id, "status": sub.status}

@router.get("/submissions")
def submissions(db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.scalars(select(Submission).where(Submission.user_id == user.id).order_by(Submission.created_at.desc()).limit(100))
    return [{"id":s.id,"challenge_id":s.challenge_id,"language":s.language,"status":s.status,"verdict":s.verdict,"score":s.score,"results":s.results,"created_at":s.created_at} for s in rows]

@router.get("/submissions/{submission_id}")
def submission_detail(submission_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    s = db.get(Submission, submission_id)
    if not s or s.user_id != user.id: raise HTTPException(404, "Submission not found")
    return {"id":s.id,"challenge_id":s.challenge_id,"language":s.language,"status":s.status,"verdict":s.verdict,"score":s.score,"results":s.results,"created_at":s.created_at}

@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user: User = Depends(current_user)):
    total = db.scalar(select(func.count(Submission.id)).where(Submission.user_id == user.id)) or 0
    accepted = db.scalar(select(func.count(Submission.id)).where(Submission.user_id == user.id, Submission.verdict == "Accepted")) or 0
    return {"total_submissions":total,"accepted":accepted,"acceptance_rate":round(accepted*100/total) if total else 0}

@router.post("/review")
def review(payload: SubmitIn, user: User = Depends(current_user)):
    return review_code(payload.language, payload.source_code)

@router.get("/leaderboard")
def leaderboard(db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.execute(select(User.id, User.name, func.count(Submission.id).label("accepted")).join(Submission, Submission.user_id == User.id).where(Submission.verdict == "Accepted").group_by(User.id, User.name).order_by(func.count(Submission.id).desc()).limit(20)).all()
    return [{"user_id": row.id, "name": row.name, "accepted": row.accepted} for row in rows]
