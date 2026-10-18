# PrivacyAudit AI

**AI-Powered Privacy Impact Assessment & DPDP Compliance Assistant**

A full-stack web platform that helps organizations discover personal-data risks, assess privacy controls against configurable DPDP requirements, and track remediation — all from one intelligent dashboard.

---

## Features

- **Document Upload**: Drag-and-drop support for PDF, DOCX, XLSX, CSV, TXT, PNG, JPG
- **Text Extraction**: Automatic extraction with OCR fallback for scanned documents
- **PII Detection**: Multi-layer engine using regex, spaCy NER, and contextual analysis with confidence scoring
- **Compliance Assessment**: Configurable DPDP rule engine with 12 controls (PASS/PARTIAL/FAIL/NOT_ASSESSED)
- **Risk Scoring**: Deterministic weighted risk engine (0-100) — never LLM-only
- **Data Flow Mapping**: Automatic extraction of processing activities and data flows
- **AI Assistant**: RAG-based chat using ChromaDB vector search + Ollama LLM
- **Remediation Management**: Kanban-style task board with assignments and progress tracking
- **Audit Reports**: Professional PDF generation with evidence, disclaimers, and limitations
- **Dashboard**: Real-time privacy posture with Recharts visualizations
- **Role-Based Access**: Admin, Privacy Officer, Auditor, Employee roles
- **Dark/Light Mode**: Full theme support

---

## Architecture

```
privacy-audit-ai/
├── backend/          FastAPI + SQLAlchemy + SQLite (PostgreSQL-ready)
│   ├── app/
│   │   ├── api/routes/    REST API endpoints
│   │   ├── core/          Config, security, logging
│   │   ├── database/      SQLAlchemy models & connection
│   │   ├── schemas/       Pydantic request/response models
│   │   ├── services/      Business logic (PII, compliance, risk, LLM, etc.)
│   │   ├── ai/            Prompts and chains
│   │   ├── rules/         Configurable DPDP controls JSON
│   │   └── utils/         File handling, masking, validation
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/         React 18 + Vite + Tailwind CSS + Recharts
│   ├── src/
│   │   ├── components/    Reusable UI components
│   │   ├── pages/         Route pages (Dashboard, Documents, Chat, etc.)
│   │   ├── layouts/       Sidebar layout
│   │   ├── contexts/      Auth context
│   │   └── services/      API service layer
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
├── data/             Uploads, reports, ChromaDB vectors
├── docs/             Architecture, API, setup documentation
└── docker-compose.yml
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Tailwind CSS, React Router, Axios, Recharts, Lucide React, React Dropzone, Framer Motion |
| Backend | Python 3.11, FastAPI, Uvicorn, Pydantic, SQLAlchemy |
| Database | SQLite (prototype) — PostgreSQL-ready architecture |
| AI/NLP | Ollama (Llama 3), spaCy, regex, rule-based NLP |
| Vectors | ChromaDB with organization isolation |
| OCR | Tesseract OCR, pytesseract, pdf2image |
| Documents | pdfplumber, python-docx, openpyxl |
| Reports | reportlab (PDF generation) |
| Security | JWT (python-jose), bcrypt (passlib) |

---

## Prerequisites

- **Python 3.11+**
- **Node.js 20+**
- **Tesseract OCR** (for image/PDF OCR)
- **Ollama** (optional — app works without it using deterministic fallback)

---

## Installation

### 1. Clone & Setup Environment

```bash
cd privacy-audit-ai
cp .env.example .env
# Edit .env with your settings
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt

# Optional: download spaCy English model
python -m spacy download en_core_web_sm

# Run development server
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

Auto-generated docs at `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`

### 4. Tesseract OCR Installation

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr poppler-utils
```

**Windows:**
Download installer from [github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)

### 5. Ollama Setup (Optional)

```bash
# Install Ollama from https://ollama.ai

# Pull Llama 3 model
ollama pull llama3

# Start Ollama server
ollama serve
```

If Ollama is not available, the app automatically falls back to deterministic rule-based analysis.

---

## Docker Setup

```bash
# Build and run all services
docker-compose up --build

# Or run individual services
docker-compose up backend
docker-compose up frontend
docker-compose up ollama
```

---

## Demo Mode

The application works **fully without Ollama**. All core analysis uses deterministic rules:

1. Set `OLLAMA_ENABLED=false` in `.env`
2. Register an account at `/register`
3. Upload sample documents from `sample_documents/`
4. Click "Analyze" on extracted documents
5. View findings, risks, and remediation recommendations

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new organization + admin user |
| POST | `/api/auth/login` | Login and receive JWT token |
| POST | `/api/documents/upload` | Upload document (multipart/form-data) |
| GET | `/api/documents` | List organization documents |
| POST | `/api/analysis/{id}/start` | Start privacy analysis (background) |
| GET | `/api/analysis/{id}` | Get analysis results with findings |
| GET | `/api/findings` | List findings with filters |
| PATCH | `/api/findings/{id}` | Update finding status |
| GET | `/api/dashboard` | Dashboard summary + charts data |
| POST | `/api/remediation` | Create remediation task |
| GET | `/api/remediation` | List remediation tasks |
| PATCH | `/api/remediation/{id}` | Update task status |
| POST | `/api/chat` | AI compliance assistant query |
| POST | `/api/reports/generate` | Generate PDF audit report |
| GET | `/api/health` | Health check + service status |

---

## User Roles

| Role | Permissions |
|------|------------|
| **ADMIN** | Full access: users, audits, rules, settings, deletion |
| **PRIVACY_OFFICER** | Upload, assess, review, create tasks, generate reports, chat |
| **AUDITOR** | View documents, findings, risks, reports, add comments |
| **EMPLOYEE** | View dashboards, assigned tasks, update task status |

---

## Security Features

- JWT authentication with secure bcrypt password hashing
- Role-based access control (RBAC) on all API endpoints
- Organization isolation — users cannot access other orgs' data
- SHA-256 file hashing for integrity verification
- MIME type and extension validation
- Path traversal protection
- Secure filename generation
- PII masking in UI, logs, and AI responses
- No raw PII in application logs
- CORS configuration
- Environment variables for secrets

---

## PII Detection Categories

- **Identity**: Name, username, employee ID
- **Contact**: Email, phone, address
- **Government IDs**: Aadhaar, PAN, passport, driving license
- **Financial**: Bank account, IFSC, credit card
- **Location**: Address, PIN code, GPS
- **Online**: IP address, device ID, cookie ID
- **Employment**: Employee records, salary
- **Health**: Medical records
- **Education**: Student ID, grades

---

## Compliance Controls

The system includes 12 configurable DPDP-inspired controls:

1. Notice and Transparency
2. Purpose Limitation
3. Data Minimization
4. Retention and Deletion
5. Security Safeguards
6. Third-Party Processor Management
7. Cross-Border Transfer Controls
8. Consent Management
9. Data Subject Rights
10. Breach Notification
11. Children's Data Protection
12. Sensitive Personal Data

Controls are stored in `backend/app/rules/dpdp_controls.json` and can be updated without code changes.

---

## Risk Scoring Methodology

Risk Score (0-100) is calculated from weighted deterministic factors:

| Factor | Weight | Description |
|--------|--------|-------------|
| Sensitive Data | 25 | Presence of sensitive categories |
| External Sharing | 20 | Third-party/processor references |
| Retention Gap | 15 | Missing retention documentation |
| Security Gap | 15 | Missing security controls |
| Evidence Gap | 10 | Compliance control failures |
| Cross-Border | 10 | International transfer references |
| Volume Exposure | 5 | Document scope indicator |

**Severity Thresholds:**
- 0-24: LOW
- 25-49: MEDIUM
- 50-74: HIGH
- 75-100: CRITICAL

---

## Limitations

- OCR quality depends on Tesseract and document scan quality
- LLM features require local Ollama instance (optional)
- SQLite for prototype — migrate to PostgreSQL for production multi-user scale
- spaCy NER is optional; falls back to regex-only detection
- Analysis is AI-assisted, not a replacement for legal professionals

---

## Deployment

### Frontend (Vercel)
```bash
cd frontend
npm run build
# Deploy `dist/` folder to Vercel
```

### Backend (Render/Railway/Docker)
```bash
cd backend
docker build -t privacyaudit-backend .
docker run -p 8000:8000 -e JWT_SECRET_KEY=your-secret privacyaudit-backend
```

---

## License

MIT License — see LICENSE file for details.

---

## Disclaimer

**This assessment is generated using automated rules, document analysis, and AI-assisted reasoning. It is intended to support privacy and compliance review and does not constitute legal advice or a definitive determination of compliance. Professional/legal review is recommended for all high-impact decisions.**
