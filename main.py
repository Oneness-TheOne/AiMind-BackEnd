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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    found = db.query(User).filter(User.userid == payload.userid).first()
    if found:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": f"{payload.userid}이 이미 있습니다"},
        )

    hashed = hash_password(payload.password)
    user = User(
        userid=payload.userid,
        password=hashed,
        name=payload.name,
        email=payload.email,
        url=payload.url,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_jwt_token(str(user.id))
    return {"token": token, "userid": payload.userid}


@app.post("/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.userid == payload.userid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": f"{payload.userid}를 찾을 수 없음"},
        )

    if not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "아이디 또는 비밀번호 확인"},
        )

    token = create_jwt_token(str(user.id))
    return {"token": token, "userid": payload.userid}


@app.post("/auth/me")
def me(context=Depends(get_current_user_context)):
    user = context["user"]
    return {"token": context["token"], "userid": user.userid}


@app.get("/post")
def get_posts(
    userid: str | None = None,
    context=Depends(get_current_user_context),
    db: Session = Depends(get_db),
):
    query = db.query(Post)
    if userid:
        query = query.filter(Post.userid == userid)
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
        userid=user.userid,
        url=user.url,
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
