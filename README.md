![Frontend Coverage](.github/badges/frontend-coverage.svg)
![Backend Coverage](.github/badges/backend-coverage.svg)
![Data Pipelines Coverage](.github/badges/data-pipelines-coverage.svg)

# AIDoctors

Your medical first point of contact

## 🌐 Live Application

**Access the application:** [https://dsoko2ogrj808.cloudfront.net](https://dsoko2ogrj808.cloudfront.net)

## 📋 Overview

AIDoctors is an AI-powered drug-drug interaction (DDI) prediction system designed to help healthcare professionals identify potential adverse drug interactions. The platform leverages machine learning models trained on real-world clinical data to provide risk assessments when prescribing multiple medications.

### Key Features

- **DDI Risk Prediction**: Analyze potential interactions between current and newly prescribed medications
- **Patient Context Analysis**: Predictions consider patient demographics, comorbidities, and medication history compared to historical cases
- **Real-time Alerts**: Receive immediate feedback on high-risk drug combinations
- **Clinical Decision Support**: Evidence-based recommendations to support safer prescribing practices

### Technology Stack

- **Frontend**: Next.js, React, TypeScript, TailwindCSS
- **Backend**: FastAPI, Python, PostgreSQL
- **ML Pipeline**: Custom fine-tuned models on FAERS and Synthea datasets
- **Infrastructure**: AWS (ECS Fargate, RDS, ALB, S3, EventBridge)
- **CI/CD**: GitHub Actions, Terraform

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

## 🚀 Getting Started

### Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/UofT-CSC490-F2025/AIDoctors.git
   cd AIDoctors
   ```

2. **Set up the application**
   - **Frontend**: See [Frontend README](src/application/frontend/README.md) for instructions on installing dependencies and running the Next.js application
   - **Backend**: See [Backend README](src/application/backend/README.md) for instructions on setting up the FastAPI server and database

### Prerequisites

- Node.js 20.9.0+ (for frontend)
- Python 3.11+ (for backend)
- PostgreSQL (for database)
- Docker (optional, for containerized development)
- AWS Credentials (for Bedrock API access)

## 🏗️ Project Structure

```
AIDoctors/
├── src/
│   ├── application/
│   │   ├── frontend/          # Next.js web application
│   │   └── backend/           # FastAPI backend service
│   ├── data_pipelines/        # Data extraction and processing
│   ├── finetune/              # Model fine-tuning scripts
│   ├── llm_eval/              # LLM evaluation utilities
│   └── rl_judge/              # Reinforcement learning training
├── terraform/                  # Infrastructure as Code
├── data/                       # Datasets (FAERS, Synthea)
└── .github/                    # CI/CD workflows
```

## 🏛️ Architecture

![Architecture Diagram for the cloud](images/architecture_diagram.png)

### Data Flow

1. **Data Extraction**: Weekly automated extraction from FAERS database
2. **Data Processing**: Transform and load into PostgreSQL
3. **Model Training**: Fine-tune models on combined datasets
4. **Prediction**: Real-time DDI risk assessment via API
5. **Frontend**: User interface for healthcare professionals

## 🧪 Testing

The project maintains comprehensive test coverage:

- **Frontend**: ![Frontend Coverage](.github/badges/frontend-coverage.svg)
- **Backend**: ![Backend Coverage](.github/badges/backend-coverage.svg)
- **Data Pipelines**: ![Data Pipelines Coverage](.github/badges/data-pipelines-coverage.svg)

Run tests:

```bash
# Frontend tests
cd src/application/frontend
npm test

# Backend tests
cd src/application/backend
uv run pytest

# Data pipeline tests
cd src/data_pipelines
pytest
```

## 🚢 Deployment

### Infrastructure

The application is deployed on AWS using Terraform:

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Key AWS services used:

- **ECS Fargate**: Container orchestration
- **RDS PostgreSQL**: Database
- **ALB**: Load balancing
- **S3**: Data storage
- **EventBridge**: Scheduled tasks
- **CloudFront**: CDN for frontend

### CI/CD Pipeline

GitHub Actions automatically:

- Runs tests on pull requests
- Updates coverage badges
- Deploys to production on merge to main
- Builds and pushes Docker images to ECR

## 📊 Data Sources

- **FAERS**: FDA Adverse Event Reporting System
- **Synthea**: Synthetic patient data generator
- **DDI Database**: Drug-drug interaction reference tables

## 🔐 Security & Privacy

- JWT-based authentication
- Role-based access control (RBAC)
- Encrypted data transmission (TLS)
- No storage of patient identifiable information (PII)

## 📝 License

This project is licensed under the terms specified in [LICENSE](LICENSE).

## 👥 Contributors

Developed by the AIDoctors team at University of Toronto.

## 🙋 Support

For issues, questions, or contributions:

- Open an issue on GitHub
- Contact the development team
- Review component-specific READMEs for detailed documentation

## 🔗 Related Documentation

- [Frontend Documentation](src/application/frontend/README.md)
- [Backend Documentation](src/application/backend/README.md)
- [Data Pipeline Documentation](src/data_pipelines/)
- [ML Training Guide](src/rl_judge/README_LOGGING.md)
- [Terraform Infrastructure](terraform/README.md)
