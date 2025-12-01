![Frontend Coverage](.github/badges/frontend-coverage.svg)
![Backend Coverage](.github/badges/backend-coverage.svg)
![Data Pipelines Coverage](.github/badges/data-pipelines-coverage.svg)

# AIDoctors

Your medical first point of contact

## 🌐 Live Application

**Access the application:** [https://main.d3jxl3jzen5r8m.amplifyapp.com](https://main.d3jxl3jzen5r8m.amplifyapp.com)

## 📋 Overview

AIDoctors is an AI-powered drug-drug interaction (DDI) prediction system designed to help healthcare professionals identify potential adverse drug interactions. The platform leverages machine learning models trained on real-world clinical data to provide risk assessments when prescribing multiple medications.

### Key Features

-   **DDI Risk Prediction**: Analyze potential interactions between current and newly prescribed medications
-   **Patient Context Analysis**: Consider patient demographics, comorbidities, and medication history
-   **Real-time Alerts**: Receive immediate feedback on high-risk drug combinations
-   **Clinical Decision Support**: Evidence-based recommendations to support safer prescribing practices

### Technology Stack

-   **Frontend**: Next.js, React, TypeScript, TailwindCSS
-   **Backend**: FastAPI, Python, PostgreSQL
-   **ML Pipeline**: Custom fine-tuned models on FAERS and Synthea datasets
-   **Infrastructure**: AWS (ECS Fargate, RDS, ALB, S3, EventBridge)
-   **CI/CD**: GitHub Actions, Terraform

### Architecture

The application consists of three main components:

1. **Web Application** (Frontend + Backend API)

    - User authentication and session management
    - Interactive prediction interface
    - RESTful API for DDI predictions

2. **Data Extraction Pipeline**

    - Automated extraction from FAERS database
    - Scheduled via EventBridge (weekly)
    - Processes adverse event reports

3. **ML Training Pipeline**
    - Model fine-tuning on combined datasets
    - Scheduled via EventBridge (weekly, 30min after extraction)
    - Continuous model improvement
