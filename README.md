# Nestra MVP — Smart Home Device Management

A modern platform for smart home device management and intelligent automation with a backend API, AI reasoning service, and interactive React frontend.

---

## 📁 Project Structure

```
nestra-mvp/
├── backend/              # API service for device management
├── intelligence/         # AI reasoning service
├── frontend/             # React/Next.js UI
├── shared/               # Shared utilities
└── migrations/           # Database migrations
```

---

## 🔧 Backend Service

RESTful API for device management, integrations, and state synchronization built with FastAPI.

### Running Locally

```bash
cd backend
python -m uvicorn src.main:app --reload
# API documentation available at /docs
```

---

## 🧠 Intelligence Service

AI-powered reasoning service for interpreting device state and executing automations.

### Running Locally

```bash
cd intelligence
python -m uvicorn src.main:app --reload
```

---

## 🎨 Frontend

Interactive React/Next.js UI for managing devices and automations.

### Running Locally

```bash
cd frontend
npm install
npm start
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 15+

### Development Setup

```bash
# Start backend
cd backend && python -m uvicorn src.main:app --reload &

# Start intelligence service
cd intelligence && python -m uvicorn src.main:app --reload &

# Start frontend
cd frontend && npm start
```

---

## 📚 Technology Stack

| Component    | Stack                            |
| ------------ | -------------------------------- |
| Frontend     | React 18, Next.js 14, TypeScript |
| Backend      | FastAPI, SQLAlchemy, PostgreSQL  |
| Intelligence | Python 3.12, Claude API          |
| Database     | PostgreSQL 15                    |

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feat/NEM-XX-description`
2. Commit with format: `NEM-XX: lowercase description`
3. Push and open a PR

Pre-commit hooks enforce code quality standards.

---

**Maintainer:** Akin Ola
