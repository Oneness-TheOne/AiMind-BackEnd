
from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from auth import create_jwt_token, get_current_user_context, hash_password, verify_password
from db import get_db, init_db
from db_models import Post, User
from models import LoginRequest, SignupRequest, PostCreateRequest, PostUpdateRequest
from utils import serialize_post, serialize_posts

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_origin_regex=r"^http://(localhost|127\\.0\\.0\\.1)(:\\d+)?$",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    found = db.query(User).filter(User.email == payload.email).first()
    if found:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "회원이 있습니다!"},
        )

    hashed = hash_password(payload.password)
    user = User(
        password=hashed,
        name=payload.name,
        email=payload.email,
        agree_terms=1 if payload.agree_terms else 0,
        agree_privacy=1 if payload.agree_privacy else 0,
        agree_marketing=1 if payload.agree_marketing else 0,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_jwt_token(str(user.id))
    return {"token": token, "email": user.email}



@app.post("/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "회원정보가 없습니다!"},
        )

    if not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "비밀번호를 확인하세요!"},
        )

    token = create_jwt_token(str(user.id))
    return {"token": token, "email": payload.email}


@app.post("/auth/me")
def me(context=Depends(get_current_user_context)):
    user = context["user"]
    return {"token": context["token"], "email": user.email}


@app.get("/post")
def get_posts(
    email: str | None = None,
    context=Depends(get_current_user_context),
    db: Session = Depends(get_db),
):
    query = db.query(Post)
    if email:
        query = query.filter(Post.userid == email)
    data = query.order_by(Post.createdAt.desc()).all()
    return serialize_posts(data)


@app.get("/post/{post_id}")
def get_post(
    post_id: str,
    context=Depends(get_current_user_context),
    db: Session = Depends(get_db),
):
    try:
        post_id_int = int(post_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"{post_id}의 포스트가 없습니다"},
        )
    post = db.query(Post).filter(Post.id == post_id_int).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"{post_id}의 포스트가 없습니다"},
        )
    return serialize_post(post)


@app.post("/post", status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreateRequest,
    context=Depends(get_current_user_context),
    db: Session = Depends(get_db),
):
    user = context["user"]
    now = datetime.utcnow()
    post = Post(
        text=payload.text,
        userIdx=user.id,
        name=user.name,
        userid=user.email,
        createdAt=now,
        updatedAt=now,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return serialize_post(post)


@app.put("/post/{post_id}")
def update_post(
    post_id: str,
    payload: PostUpdateRequest,
    context=Depends(get_current_user_context),
    db: Session = Depends(get_db),
):
    user = context["user"]
    try:
        post_id_int = int(post_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"{post_id}에 대한 포스트가 없습니다"},
        )
    existing = db.query(Post).filter(Post.id == post_id_int).first()
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"{post_id}에 대한 포스트가 없습니다"},
        )
    if existing.userIdx != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    existing.text = payload.text
    existing.updatedAt = datetime.utcnow()
    db.commit()
    db.refresh(existing)
    return serialize_post(existing)


@app.delete("/post/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: str,
    context=Depends(get_current_user_context),
    db: Session = Depends(get_db),
):
    user = context["user"]
    try:
        post_id_int = int(post_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"{post_id}에 대한 포스트가 없습니다"},
        )
    existing = db.query(Post).filter(Post.id == post_id_int).first()
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"{post_id}에 대한 포스트가 없습니다"},
        )
    if existing.userIdx != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    db.delete(existing)
    db.commit()
    return None
