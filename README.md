# AiMind BackEnd (FastAPI)

## Environment variables

Create a `.env` file in this folder and set at least:

```bash
# Auth
JWT_SECRET=...
JWT_EXPIRES_SEC=172800
BCRYPT_SALT_ROUNDS=10

# MySQL
DB_HOST=...
DB_PORT=3306
DB_NAME=AiMind
DB_USER=...
DB_PASSWORD=...

# MongoDB (Beanie)
MONGODB_URI=...
MONGODB_DB_NAME=aimind

# S3
S3_BUCKET=...
S3_REGION=...
S3_ACCESS_KEY_ID=...
S3_SECRET_ACCESS_KEY=...
# Optional
S3_PUBLIC_BASE_URL=

# AI Models service (for /diary-ocr OCR extraction)
AIMODELS_BASE_URL=http://localhost:8080
```

## Diary OCR API

All endpoints below require `Authorization: Bearer <token>`.

- `POST /diary-ocr` (multipart form)
  - fields: `file` (image), `area` (string, optional)
  - behavior: uploads the image to S3 + calls AI Models `/diary-ocr` + stores result in MongoDB collection `diary_ocr`

- `GET /diary-ocr?user_id=123`
  - returns: latest-first list of saved diary OCR entries

- `GET /diary-ocr/{entry_id}`
  - returns: one diary OCR entry (image_url + texts)

