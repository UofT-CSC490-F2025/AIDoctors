# AI Doctors Frontend

Next.js 15 app that connects to the FastAPI backend to surface patient-specific drug–drug interaction (DDI) alerts.

## Key pages

- `/` – marketing overview of the project
- `/login` and `/signup` – email/password auth, JWT stored in an HTTP-only `access_token` cookie
- `/dashboard` – protected overview of the integration
- `/dashboard/predict` – protected form to send patient context to the backend and render top-k alerts

## Configuration

Set `NEXT_PUBLIC_API_BASE_URL` in `.env` to the running FastAPI backend base URL (e.g., `http://localhost:8000` for dev environment)

## Running locally

```bash
npm install
npm run dev
```
