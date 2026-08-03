<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Shrinidhi857/Theoria-AI">
    <img src="theoria-frontend/public/Theoria.svg" alt="Logo" width="90" height="90">
  </a>

  <h3 align="center">Theoria AI</h3>

  <p align="center">
    An intelligent AI-powered mathematical and scientific animation platform.
    <br />
    Transform complex equations, algorithms, and theoretical concepts into beautiful, narrated Manim animations.
    <br />
    <br />
    <a href="https://github.com/Shrinidhi857/Theoria-AI">View Demo</a>
    ·
    <a href="https://github.com/Shrinidhi857/Theoria-AI/issues">Report Bug</a>
    ·
    <a href="https://github.com/Shrinidhi857/Theoria-AI/issues">Request Feature</a>
    ·
    <a href="https://github.com/Shrinidhi857/Theoria-AI/tree/main/theoria-frontend">Frontend App</a>
  </p>

  <!-- BADGES -->
  <p align="center">
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.9%2B-3776AB.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
    <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"></a>
    <a href="https://react.dev/"><img src="https://img.shields.io/badge/React-19.0-61DAFB.svg?style=for-the-badge&logo=react&logoColor=black" alt="React 19"></a>
    <a href="https://www.typescriptlang.org/"><img src="https://img.shields.io/badge/TypeScript-5.0%2B-3178C6.svg?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript"></a>
    <a href="https://ai.google.dev/"><img src="https://img.shields.io/badge/Google_Gemini-2.5-4285F4.svg?style=for-the-badge&logo=google&logoColor=white" alt="Google Gemini"></a>
    <a href="https://www.manim.community/"><img src="https://img.shields.io/badge/Manim-Community-ECEFF4.svg?style=for-the-badge&logo=manim&logoColor=black" alt="Manim"></a>
    <a href="https://tailwindcss.com/"><img src="https://img.shields.io/badge/Tailwind_CSS-v4-38BDF8.svg?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="Tailwind CSS"></a>
    <a href="https://github.com/Shrinidhi857/Theoria-AI/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="License"></a>
  </p>
</div>

---

## 📖 Table of Contents
- [About The Project](#-about-the-project)
- [Key Features](#-key-features)
- [Architecture & Server Entrypoint](#-architecture--server-entrypoint-mainpy)
- [AI Video Generation Pipeline](#-ai-video-generation-pipeline)
- [Tech Stack & Badge Showcase](#-tech-stack)
- [Backend Dependencies Breakdown](#-backend-dependencies-requirements-txt)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Project Directory Structure](#-project-structure)
- [Contributing & License](#-contributing)

---

## 📖 About The Project

**Theoria AI** is an end-to-end AI teaching engine and animation platform designed to automate the creation of high-quality mathematical, scientific, and computer science visual lessons. 

Given an algorithmic or mathematical prompt (e.g. *"Explain Binary Search on an array [2, 5, 8, 12, 16, 23] with target 23"*), Theoria AI:
1. **Deconstructs the Problem**: Extracts parameters, formulates naive vs. optimal approach strategy using **Google Gemini 2.5**.
2. **Generates Animation DSL**: Converts visual concepts into validated Manim script instructions.
3. **Renders Video**: Executes **Manim Engine** to produce 60fps MP4 video clips.
4. **Synthesizes Audio**: Generates synchronized voice narration using **gTTS** (Google Text-to-Speech).
5. **Muxes & Serves Output**: Merges audio and video via **FFmpeg** and serves the complete video lesson over a high-performance **FastAPI** backend to a **React 19** frontend.

---

## ✨ Key Features

- **🔐 Secure Authentication System**
  - **Google OAuth 2.0 Integration**: One-click authentication with Google.
  - **JWT Authentication**: Access and refresh tokens with salted `bcrypt` password hashing.
  - **User History Persistence**: Store generated animations in user accounts via SQLite/PostgreSQL.

- **🎬 Automated AI Teaching Pipeline**
  - **Parameter & Data Extraction**: Automatically detects target numbers, array elements, and problem constraints.
  - **LLM Reasoning Loop**: Generates structured step-by-step thinking for problem solving.
  - **DSL Validation**: Robust syntax checker (`DSLValidator`) to eliminate Manim rendering errors.

- **🎙️ Voice Narration & Audio Sync**
  - **Dynamic Text-to-Speech**: Generates natural speech narration matching scene descriptions.
  - **FFmpeg Merger**: Syncs frame rates and audio clips seamlessly into final rendered `.mp4` video files.

- **🖥️ Interactive React Visual Studio**
  - **Real-Time Pipeline Visualizer**: View live progress through parameter extraction, thinking, rendering, and audio merge.
  - **Interactive Player**: Watch, pause, inspect generated Manim Python code, and download rendered files.
  - **History Dashboard**: Browse, filter, and re-watch previously generated animation lessons.

---

## 🏛️ Architecture & Server Entrypoint (`main.py`)

The backend entrypoint resides in [`backend/app/main.py`](file:///c:/code-2026/Theoria%20AI/backend/app/main.py). It orchestrates the FastAPI application lifespan, static media serving, database initialization, and router configuration:

```python
# Key Application Lifecycle & Router Configuration in main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler initializing DB tables and ensuring output directory exists."""
    logger.info("Initializing Database Tables...")
    init_db()
    
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
    os.makedirs(output_dir, exist_ok=True)
    yield
    logger.info("Shutting down Application...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    lifespan=lifespan
)

# Serves rendered video output files at /output
app.mount("/output", StaticFiles(directory=output_path), name="output")

# API v1 Router Registration
app.include_router(api_v1_router, prefix=settings.API_V1_STR)
```

### Core Responsibilities of `app/main.py`:
- **Lifespan Management**: Automatically initializes database schemas (`init_db()`) and verifies the output storage directory (`/output`) on startup.
- **Static File Mounting**: Serves output `.mp4` video files directly over HTTP (`/output/{filename}`) so the React frontend can stream them.
- **CORS Middleware**: Manages cross-origin resource sharing for seamless local development between Vite frontend (`http://localhost:5173`) and FastAPI (`http://localhost:8000`).
- **Interactive Documentation**: Auto-generates OpenAPI (`/api/v1/docs`) and ReDoc (`/api/v1/redoc`) API reference pages.

---

## 🔄 AI Video Generation Pipeline

The heart of the AI Teaching Engine is located in `backend/engine/pipeline.py`. It executes an 8-stage automated workflow:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   USER PROMPT INPUT                                    │
│                 "Explain Binary Search on [2, 5, 8, 12, 16, 23] target 23"               │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
 1. Lesson Planner         ──► Extracts algorithm, input arrays, search targets using Gemini
                                            │
 2. Scene Planner          ──► Breaks topic into intuitive visual scenes & narration scripts
                                            │
 3. Animation Planner      ──► Generates structured Animation DSL JSON schema
                                            │
 4. DSL Validator          ──► Validates Manim object positioning, colors, & layout logic
                                            │
 5. Manim Code Generator   ──► Compiles valid DSL JSON into pure Python Manim script
                                            │
 6. Manim Renderer         ──► Runs Manim CLI engine to render raw MP4 video clip
                                            │
 7. Narration Generator    ──► Synthesizes voiceover audio (.mp3) using gTTS
                                            │
 8. FFmpeg Merger          ──► Merges video clip & TTS audio into final output asset (.mp4)
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              FINAL OUTPUT VIDEO LESSON                                 │
│                              output/final_lesson_xyz.mp4                               │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Tech Stack

### Frontend Technologies
[![React](https://img.shields.io/badge/React-19.0-61DAFB.svg?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0%2B-3178C6.svg?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-6.0-646CFF.svg?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-v4.0-38BDF8.svg?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Lucide](https://img.shields.io/badge/Lucide_Icons-React-F56565.svg?style=for-the-badge&logo=react&logoColor=white)](https://lucide.dev/)

### Backend & AI Technologies
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285F4.svg?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Manim](https://img.shields.io/badge/Manim-Community_Edition-ECEFF4.svg?style=for-the-badge&logo=manim&logoColor=black)](https://www.manim.community/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15.0-336791.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.sqlalchemy.org/)

### Audio & Multimedia Processing
[![gTTS](https://img.shields.io/badge/gTTS-Google_Text_To_Speech-4285F4.svg?style=for-the-badge&logo=google&logoColor=white)](https://pypi.org/project/gTTS/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Media_Muxer-0078D7.svg?style=for-the-badge&logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2.0-E92063.svg?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)

---

## 📦 Backend Dependencies (`requirements.txt`)

The [`backend/requirements.txt`](file:///c:/code-2026/Theoria%20AI/backend/requirements.txt) file specifies the foundational packages driving the backend:

```ini
manim>=0.18.0          # Mathematical Animation Engine for 2D/3D video rendering
google-genai>=0.1.0    # Google Gemini 2.5 SDK for LLM lesson & animation planning
pydantic>=2.0.0        # Data validation and settings management
gTTS>=2.5.0            # Google Text-to-Speech voice narration generator
fastapi>=0.100.0       # Asynchronous high-performance REST API web framework
uvicorn>=0.20.0        # ASGI web server implementation
imageio-ffmpeg>=0.4.0  # Python bindings for FFmpeg video/audio processing
sqlalchemy>=2.0.0      # SQL Toolkit & Object Relational Mapper
psycopg2-binary>=2.9.0 # PostgreSQL database adapter
pyjwt[crypto]>=2.8.0   # JSON Web Token authentication encoding & decoding
passlib[bcrypt]>=1.7.4 # Password hashing algorithm
google-auth>=2.25.0    # Google OAuth 2.0 authentication integration
```

---

## 🚀 Getting Started

### Prerequisites

Ensure the following tools are installed on your workstation:
- **Python**: `3.9` or higher
- **Node.js**: `18.0` or higher
- **FFmpeg**: System-wide binary available in system PATH
- **Manim**: Community Edition (`pip install manim`)

---

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment:**
   - **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - **Windows:**
     ```cmd
     python -m venv venv
     venv\Scripts\activate
     ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Fill in your credentials:
   ```env
   GEMINI_API_KEY=your_google_gemini_api_key
   SECRET_KEY=your_super_secret_jwt_signing_key
   DATABASE_URL=sqlite:///./theoria.db
   ```

5. **Launch the FastAPI Server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   Access API documentation at `http://localhost:8000/api/v1/docs`.

---

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd theoria-frontend
   ```

2. **Install Node modules:**
   ```bash
   npm install
   ```

3. **Launch the React 19 Dev Server:**
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173` in your browser.

---

## 📁 Project Structure

```
Theoria-AI/
├── README.md                           # Main Project Documentation
├── backend/
│   ├── app/
│   │   ├── api/                        # REST API endpoints
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── auth.py         # Login, Register, Google OAuth
│   │   │       │   ├── engine.py       # Video generation endpoints
│   │   │       │   └── users.py        # User profile endpoints
│   │   │       └── router.py           # V1 API router aggregator
│   │   ├── core/                       # JWT Security & Settings
│   │   ├── db/                         # Database connection & init
│   │   ├── models/                     # SQLAlchemy User & Video Models
│   │   ├── schemas/                    # Pydantic Request/Response schemas
│   │   ├── services/                   # Engine & Auth Service Layer
│   │   └── main.py                     # FastAPI application entrypoint & static mount
│   ├── engine/                         # AI Teaching & Manim Engine
│   │   ├── animation_planner.py        # Animation DSL Generator
│   │   ├── dsl_validator.py            # DSL Syntax & Safety Validator
│   │   ├── ffmpeg_merge.py             # Audio-Video FFmpeg Muxer
│   │   ├── gemini_client.py            # Gemini 2.5 Client Wrapper
│   │   ├── lesson_planner.py           # Parameter extraction & strategy planning
│   │   ├── manim_generator.py          # Python code compilation from DSL
│   │   ├── narration.py                # gTTS Narration Generator
│   │   ├── pipeline.py                 # 8-step end-to-end video orchestration
│   │   └── renderer.py                 # Manim renderer execution
│   ├── output/                         # Rendered MP4 & audio files storage
│   └── requirements.txt                # Python backend dependencies
└── theoria-frontend/
    ├── public/
    │   └── Theoria.svg                 # Theoria AI Logo
    ├── src/
    │   ├── components/                 # Reusable UI components
    │   ├── context/                    # React Context (Auth State)
    │   ├── pages/                      # LandingPage, GeneratorPage, HistoryPage, ProfilePage
    │   ├── services/                   # API HTTP client & service endpoints
    │   └── utils/                      # Constants, storage, and helper functions
    └── package.json                    # Frontend Node dependencies & scripts
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to report issues or submit pull requests to enhance animation capabilities, DSL options, or UI features.

1. Fork the Repository
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

Distributed under the MIT License. See [`LICENSE`](https://github.com/Shrinidhi857/Theoria-AI/blob/main/LICENSE) for more information.
