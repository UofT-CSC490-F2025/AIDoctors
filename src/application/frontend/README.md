# AI Doctors Frontend

Next.js 15 app that connects to the FastAPI backend to surface patient-specific drug–drug interaction (DDI) alerts.

## Key pages

- `/` – marketing overview of the project
- `/login` and `/signup` – email/password auth, JWT stored in an HTTP-only `access_token` cookie
- `/dashboard` – protected overview of the integration
- `/dashboard/predict` – protected form to send patient context to the backend and render top-k alerts

## Setup

Install the dependencies:

```bash
npm install
```

Set `NEXT_PUBLIC_API_BASE_URL` in `.env` to the running FastAPI backend base URL. For example:

```.env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Running Locally

Run the following command to spin up the development server:

```bash
npm run dev
```

## Production Build

Run the following command to build a static export of the frontend:

```bash
npm run build
```

This exports raw HTML/CSS/JS files and assets into the folder `out`. This folder can now be deployed on any HTTP server.
