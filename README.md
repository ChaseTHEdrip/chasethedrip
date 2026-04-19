# chasethedrip – File Upload App

A minimal full-stack file upload application.

## Stack

| Layer    | Technology              |
|----------|-------------------------|
| Backend  | Python · FastAPI        |
| Frontend | Next.js · React · Tailwind CSS |

---

## Backend

### Setup

```bash
cd backend
cp ../backend.env.example .env
pip install -r requirements.txt
uvicorn main:app --reload
```

The API runs on **http://localhost:8000** by default.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/upload` | Upload one or more files (multipart/form-data) |
| `GET`  | `/files` | List all uploaded files |
| `GET`  | `/files/{filename}` | Download a file |
| `DELETE` | `/files/{filename}` | Delete a file |

---

## Frontend

### Setup

```bash
cd frontend
npm install
# Set the backend URL if it differs from the default:
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

The UI runs on **http://localhost:3000** by default.

### Features

- Drag-and-drop or click-to-select file upload
- Multi-file upload in a single request
- Browse and download previously uploaded files
- Delete individual files
