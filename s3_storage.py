import io
import os
from uuid import uuid4

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException, UploadFile, status
from PIL import Image

from config import settings

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_DIMENSION = 1024


def _build_public_url(key: str) -> str:
    if settings.s3_public_base_url:
        return f"{settings.s3_public_base_url.rstrip('/')}/{key}"
    if settings.s3_region == "us-east-1":
        return f"https://{settings.s3_bucket}.s3.amazonaws.com/{key}"
    return f"https://{settings.s3_bucket}.s3.{settings.s3_region}.amazonaws.com/{key}"


def _build_object_key(user_id: int, filename: str | None, content_type: str | None) -> str:
    ext = ""
    if content_type in ALLOWED_IMAGE_TYPES:
        ext = ALLOWED_IMAGE_TYPES[content_type]
    elif filename:
        _, guessed = os.path.splitext(filename)
        if guessed and len(guessed) <= 10:
            ext = guessed.lower()
    return f"users/{user_id}/profile/{uuid4().hex}{ext}"


def _get_s3_client():
    return boto3.client(
        "s3",
        region_name=settings.s3_region,
        aws_access_key_id=settings.s3_access_key_id,
        aws_secret_access_key=settings.s3_secret_access_key,
    )


def _reencode_image(contents: bytes, content_type: str) -> bytes:
    image = Image.open(io.BytesIO(contents))
    image.load()

    if content_type == "image/jpeg" and image.mode != "RGB":
        image = image.convert("RGB")

    max_dim = MAX_DIMENSION
    while True:
        resized = image.copy()
        resized.thumbnail((max_dim, max_dim))

        output = io.BytesIO()
        if content_type == "image/png":
            resized.save(output, format="PNG", optimize=True, compress_level=9)
        elif content_type == "image/webp":
            resized.save(output, format="WEBP", quality=85, method=6)
        else:
            if resized.mode != "RGB":
                resized = resized.convert("RGB")
            resized.save(output, format="JPEG", quality=85, optimize=True, progressive=True)

        data = output.getvalue()
        if len(data) <= MAX_IMAGE_BYTES or max_dim <= 320:
            return data
        max_dim = int(max_dim * 0.8)


async def upload_profile_image_to_s3(upload: UploadFile, user_id: int) -> str:
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "이미지 파일이 필요합니다"},
        )
    if upload.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail={"message": "JPEG/PNG/WEBP 이미지만 업로드 가능합니다"},
        )

    contents = await upload.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "빈 파일입니다"},
        )
    if len(contents) > MAX_IMAGE_BYTES:
        contents = _reencode_image(contents, upload.content_type)
        if len(contents) > MAX_IMAGE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail={"message": "이미지는 5MB 이하만 가능합니다"},
            )

    key = _build_object_key(user_id, upload.filename, upload.content_type)
    s3 = _get_s3_client()
    try:
        s3.put_object(
            Bucket=settings.s3_bucket,
            Key=key,
            Body=contents,
            ContentType=upload.content_type,
        )
    except (BotoCoreError, ClientError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"message": "S3 업로드에 실패했습니다", "error": str(exc)},
        )

    return _build_public_url(key)
