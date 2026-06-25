# ADR-001: Backend Language and Framework

## Context
We need to build a REST API capable of handling multipart/chunked file uploads,
communicating with Azure Blob Storage, and being easy to containerize and deploy
via CI/CD pipelines on Azure.

## Decision
We will use **Python 3.11+ with FastAPI**.

## Justification
- Native async support (`async`/`await`), critical for handling concurrent chunk uploads efficiently
- Official Azure SDK for Python (`azure-storage-blob`) is mature and well documented
- Automatic OpenAPI/Swagger documentation generation
- Built-in data validation via Pydantic, reducing boilerplate for chunk metadata validation
- Lightweight, fast to containerize (small Docker images compared to full frameworks)
- Strong ecosystem for testing (pytest) aligned with our tests/ folder structure

## Alternatives Considered
- **Django**: rejected — too heavyweight for an API-only service, includes unnecessary features (ORM admin, templating)
- **Node.js (Express/NestJS)**: rejected — viable alternative, but Python was chosen for better alignment with data-processing and scripting needs in DevOps tooling
- **.NET**: rejected — strong Azure integration but steeper learning curve and heavier setup for this project's scope