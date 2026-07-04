# ResearchMind - Autonomous Research Agent

A powerful autonomous research agent powered by AI that conducts comprehensive research, discovers insights, and builds knowledge automatically using LangGraph, Django, and React.

## Features

### 🤖 Intelligent Research
- **Multi-source searching**: Integrates Wikipedia, arXiv, web search (Serper), and RAG
- **Autonomous agent**: LangGraph-based agent with 10+ reasoning nodes
- **Memory management**: Intelligent memory with embeddings using Qdrant
- **Real-time streaming**: WebSocket integration for live research step updates

### 📊 Research Analysis
- **Multi-perspective analysis**: Gathers and synthesizes information from diverse sources
- **Contradiction detection**: Identifies conflicting information
- **Source reliability scoring**: Tracks source trustworthiness over time
- **Professional reports**: Markdown-based reports with citations and confidence scores

### 💾 Knowledge Management
- **Memory browser**: Search and explore accumulated knowledge
- **Topic tagging**: Automatic categorization of information
- **Deduplication**: Content-hash based duplicate detection
- **Reliability tracking**: Source reliability learning system

### 📅 Automation
- **Scheduled research**: Set up recurring research jobs (daily, weekly, monthly)
- **Email delivery**: Automated report delivery via email
- **Task queue**: Celery-based async task processing

### 📱 User Interface
- **Modern dashboard**: Overview of research jobs and statistics
- **Live streaming**: Watch research progress in real-time
- **Report viewer**: Rich markdown renderer with export (PDF/Word)
- **Memory explorer**: Visual exploration of accumulated knowledge

## Tech Stack

### Backend
- **Framework**: Django + Django REST Framework
- **Real-time**: Django Channels with WebSockets
- **Agent**: LangGraph + Groq LLM
- **Vector DB**: Qdrant (local disk storage)
- **Task Queue**: Celery + SQLite
- **Database**: SQLite (local development)
- **Async HTTP**: FastAPI (optional side-service)

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **WebSocket**: Native WebSocket API
- **UI Components**: Lucide React, React Markdown

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** and npm
- **Groq API Key** (for LLM)
- **Serper API Key** (for web search)

Get your keys:
- [Groq API](https://console.groq.com)
- [Serper API](https://serper.dev)

## Installation & Setup

### 1. Clone Repository
```bash
cd d:\X\researchmind
```

### 2. Backend Setup

#### Create Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Configure Environment
Copy `.env.example` to `.env` **in the project root** (`researchmind/.env`, not `backend/.env`) — `python-decouple` walks up from the backend's working directory to find it there:
```env
# Django Configuration
SECRET_KEY=django-insecure-default-secret-key-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# AI / LLM Configuration
# Get your free key at: https://console.groq.com
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.3-70b-versatile

# Search Configuration
# Get your free key at: https://serper.dev
SERPER_API_KEY=your-serper-api-key

# Email Configuration — see "Email Notifications" below for details
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=no-reply@researchmind.com
```

Other settings (database, Celery broker, Qdrant path, Channels layer) are hardcoded with working local defaults in `config/settings/base.py` and don't need to be set in `.env` for local development.

#### Run Migrations
```bash
python manage.py migrate
```

#### Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

Create `.env.local` file in `frontend/`:
```env
VITE_API_URL=http://localhost:8000
```

## Running the Application

### Option 1: Simple Local Development (All in One Terminal with Docker)

The easiest way is to use the provided docker-compose file if you have Docker:
```bash
docker-compose up -d
```

### Option 2: Manual Setup (Recommended for Development)

Open **4 terminal windows** and run:

#### Terminal 1: Backend Django/Daphne Server
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python manage.py runserver
```
Runs on `http://localhost:8000`

#### Terminal 2: Celery Worker (for async tasks)
```bash
cd backend
source venv/bin/activate

# macOS/Linux:
celery -A config worker -l info

# Windows: the default "prefork" worker pool isn't supported, use solo instead
celery -A config worker -l info --pool=solo
```
This is what actually runs research jobs — creating a job via the API/UI just queues it. Without a worker running, jobs will sit in `pending` forever.

#### Terminal 3: Frontend Development Server
```bash
cd frontend
npm run dev
```
Runs on `http://localhost:5173`

#### Terminal 4: (Optional) FastAPI Runner
```bash
cd backend
source venv/bin/activate
python fastapi_app.py
```
Runs on `http://localhost:8001`

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user (returns JWT access + refresh tokens)
- `POST /api/auth/login/` - Log in (returns JWT access + refresh tokens)
- `POST /api/auth/refresh/` - Exchange a refresh token for a new access token
- `GET /api/auth/profile/` - Get current user profile

There is no server-side logout endpoint — JWTs are stateless, so the frontend just deletes the tokens from `localStorage`.

### Research Jobs
- `GET /api/research/jobs/` - List all jobs for the current user
- `POST /api/research/jobs/` - Create a new research job (`query`, `depth`: `quick`/`deep`/`expert`, `max_iterations`) — queues it on Celery
- `GET /api/research/jobs/{id}/` - Get job details, including its report if complete
- `DELETE /api/research/jobs/{id}/` - Delete a job
- `GET /api/research/steps/{job_id}/` - List agent steps recorded for a job

### Reports
- `GET /api/research/reports/` - List reports
- `GET /api/research/reports/{id}/` - Get report details
- `GET /api/research/reports/{id}/export/pdf/` - Export report as PDF
- `GET /api/research/reports/{id}/export/docx/` - Export report as DOCX

### Memory
- `GET /api/memory/entries/` - List the current user's memory entries (`?query=<text>` runs a semantic search over them via Qdrant)
- `POST /api/memory/entries/` - Manually add a memory entry
- `GET /api/memory/entries/{id}/` - Get a memory entry's details
- `GET /api/memory/stats/` - Memory count, top topic tags, estimated storage size

### Dashboard
- `GET /api/dashboard/stats/` - Total jobs, completed jobs, total reports, total memories, average confidence score (0-1 fraction, not a percentage)

### Scheduler
- `GET /api/scheduler/jobs/` - List scheduled research
- `POST /api/scheduler/jobs/` - Create scheduled research (`query_template`, `frequency`: `daily`/`weekly`/`monthly`, `deliver_via_email`)
- `PATCH /api/scheduler/jobs/{id}/` - Update scheduled research (e.g. toggle `is_active`)
- `DELETE /api/scheduler/jobs/{id}/` - Delete scheduled research

## WebSocket Endpoints

### Research Streaming
- `ws://localhost:8000/ws/research/{job_id}/`
  - Receives JSON messages with a `type` field: `step` (one agent step — `step_number`, `step_type`, `thought`, `tool_name`, `tool_input`, `tool_output`, `tokens_used`, `duration_ms`), `complete` (`report_id`), or `error` (`message`)

## Research Depth

The `depth` field on a research job (`quick` / `deep` / `expert`) controls how thorough the agent is:

| Depth | Sub-questions | Sources per sub-question | Target report length |
|---|---|---|---|
| `quick` | 4 | 1 tool (rule-selected: web/arXiv/Wikipedia/calculator) | 500-800 words |
| `deep` | 6 | Primary tool + Wikipedia cross-check | 1200-1800 words |
| `expert` | 9 | Primary tool + Wikipedia + arXiv cross-check | 2000-3000 words |

Every claim in the final report is required to cite a source that was actually retrieved by a tool — the writer prompt is explicitly forbidden from inventing URLs. The "Sources" tab on a report shows every source considered; the "References" section in the report body itself only lists what was actually cited inline.

Higher depths make more LLM and tool calls per job (an `expert` job can take several minutes), so give `max_iterations` enough headroom (15-25) for it to finish before hitting the cap.

## Email Notifications

The `EMAIL_*` variables in `.env` control how completed report emails are delivered. This only applies to **Scheduled Research** (see the Scheduler page) with "Deliver via email" enabled — one-off jobs created from "New Research" are never emailed.

- **`EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`** (the default) doesn't send real email at all — it prints the full email (subject, HTML body) to whichever terminal is running the Celery worker. This is the safe default for local development: no credentials needed, nothing leaves your machine.
- To send **real emails**, switch to `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend` and fill in `EMAIL_HOST_USER` (your email address) and `EMAIL_HOST_PASSWORD`. For Gmail specifically, `EMAIL_HOST_PASSWORD` must be a 16-character **App Password** (Google Account → Security → 2-Step Verification → App Passwords) — your normal account password will be rejected. `EMAIL_HOST`/`EMAIL_PORT`/`EMAIL_USE_TLS` are already set correctly for Gmail's SMTP server.
- `DEFAULT_FROM_EMAIL` is the "From" address on outgoing report emails.
- Restart the Celery worker after changing any `EMAIL_*` value — it reads settings at process start.

## Testing

### Run Pytest Tests
```bash
cd backend
pytest
```

### Run Specific Test
```bash
pytest tests/test_research_models.py::TestResearchJobModel::test_create_research_job -v
```

### Generate Coverage Report
```bash
pytest --cov=. --cov-report=html
```

## Project Structure

```
researchmind/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── fastapi_app.py
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── dev.py
│   │   │   └── prod.py
│   │   ├── asgi.py
│   │   ├── wsgi.py
│   │   ├── urls.py
│   │   └── celery.py
│   ├── agent/
│   │   ├── graph.py      # LangGraph orchestration
│   │   ├── tools.py      # AI tools (search, RAG, calculator)
│   │   ├── memory.py     # Qdrant memory manager
│   │   ├── prompts.py    # LLM prompts
│   │   └── runner.py     # Agent executor
│   ├── research/
│   │   ├── models.py     # ResearchJob, Report, AgentStep, Memory
│   │   ├── views.py      # API endpoints
│   │   ├── serializers.py
│   │   ├── consumers.py  # WebSocket consumer
│   │   ├── tasks.py      # Celery tasks
│   │   ├── urls.py
│   │   └── routing.py    # WebSocket routing
│   ├── scheduler/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   ├── users/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   ├── notifications/
│   │   ├── email.py      # Email sending logic
│   │   └── templates/
│   ├── tests/            # Pytest test suite
│   └── qdrant_data/      # Local Qdrant storage
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── index.css
│   │   ├── api/
│   │   │   └── client.js    # Axios client
│   │   ├── store/
│   │   │   ├── authStore.js    # Zustand auth store
│   │   │   └── researchStore.js # Zustand research store
│   │   ├── hooks/
│   │   │   └── useWebSocket.js
│   │   ├── components/
│   │   │   └── Navbar.jsx
│   │   └── pages/
│   │       ├── Landing.jsx
│   │       ├── Login.jsx
│   │       ├── Register.jsx
│   │       ├── Dashboard.jsx
│   │       ├── NewResearch.jsx
│   │       ├── LiveResearch.jsx
│   │       ├── ReportView.jsx
│   │       ├── MemoryBrowser.jsx
│   │       ├── Scheduler.jsx
│   │       └── History.jsx
│   └── public/
│
├── .env.example
├── .gitignore
├── README.md
└── docker-compose.yml
```

## Troubleshooting

### Port Already in Use
```bash
# Find and kill process on port 8000
lsof -i :8000
kill -9 <PID>
```

### Qdrant Connection Issues
```bash
# Ensure qdrant_data directory exists
mkdir backend/qdrant_data

# Or use Docker Qdrant
docker run -p 6333:6333 qdrant/qdrant
```

### API Key Errors
- Verify `.env` file exists and has correct keys
- Check API key validity in respective services
- Restart Django server after updating `.env`

### WebSocket Connection Failed
- Ensure Django is running with Daphne/Channels
- Check WebSocket URL in frontend matches backend
- Verify firewall allows WebSocket connections

## Performance Optimization

### For Production
1. Use PostgreSQL instead of SQLite
2. Deploy Qdrant separately (Docker/Cloud)
3. Use Redis for Celery broker and cache
4. Enable Redis for Channel Layers
5. Set `DEBUG=False` in Django
6. Use WhiteNoise for static files
7. Enable HTTPS

### Scaling
- Use Gunicorn + Nginx for backend
- Use Daphne for WebSocket connections
- Separate Celery workers for task processing
- Load balancer for multiple instances

## Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Check documentation in WALKTHROUGH.md
- Review test cases for usage examples

