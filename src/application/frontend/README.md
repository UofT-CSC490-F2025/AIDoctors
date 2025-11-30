# AI Doctors Frontend

A Next.js 15 application interface for the AI Doctors platform. It connects to a FastAPI backend to predict and display patient-specific drug–drug interaction (DDI) alerts.

## Key Routes

| Route                | Description                                                                    |
| :------------------- | :----------------------------------------------------------------------------- |
| `/`                  | Marketing and project overview.                                                |
| `/login`, `/signup`  | User authentication. Uses email/password and stores JWTs in HTTP-only cookies. |
| `/dashboard`         | Protected view of the integration status.                                      |
| `/dashboard/predict` | Protected form to submit patient context and render alerts.                    |

## Prerequisites

- Node.js (v20.9.0 or higher).
- npm.

## Installation & Configuration

1.  **Install dependencies:**

    ```bash
    npm install
    ```

2.  **Configure environment:**

    Create a `.env` file in the root directory. Define the API base URL:

    ```env
    NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
    ```

## Development

Start the local development server:

```bash
npm run dev
```

The frontend will be running on `http://localhost:3000`.

## Production Build

Generate a static export of the application:

```bash
npm run build
```

This compiles raw HTML, CSS, and JS assets into the `out` directory. Deploy this folder to any static web server.

## Testing

This project uses Jest for unit testing. Test files are located in `src/__tests__`.

Run tests locally:

```bash
npm run test
```

## CI/CD Pipeline

A GitHub Actions workflow (`frontend_coverage.yaml`) automates testing on repository changes that affect the frontend.

**Workflow Behaviors:**

- **Pull Requests:** Runs tests using `npm run test:ci`. Posts a comment on the PR containing the current frontend code coverage.
- **Push to Main:** Runs tests using `npm run test:ci`. Updates the coverage badge in the root README.
