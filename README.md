# 🤖 Intelligent Chat Assistant

An AI chat application built with **FastAPI**, **Streamlit**, **Supabase**, and **Google Gemini**. 

This application features real-time responses, chat history, session management (rename/delete), and a user interface.

---

## 🚀 Features

*   **AI Responses:** Real-time text generation using Google's Gemini model.
*   **Persistent Memory:** All conversations are stored in a Supabase (PostgreSQL) database.
*   **Session Management:**
    *   Create new chat sessions.
    *   **Rename** sessions with custom titles.
    *   **Delete** old sessions and their history.
*   **Modern UI:**
    *   Clean sidebar navigation with history list.
    *   Onboarding suggestions for new chats.
    *   Avatar support for User and AI.
*   **Dockerized:** Easy deployment using Docker Compose.

---

## 🛠️ Tech Stack

*   **Frontend:** [Streamlit](https://streamlit.io/) (Python-based UI)
*   **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (High-performance API)
*   **Database:** [Supabase](https://supabase.com/) (Managed PostgreSQL)
*   **AI Model:** [Google Gemini](https://ai.google.dev/) via `google-generativeai` SDK
*   **Containerization:** Docker & Docker Compose

---

## 📋 Prerequisites

Before running the application, ensure you have the following:

1.  **Docker Desktop** installed and running.
2.  A **Supabase** account (Free tier is fine).
3.  A **Google AI Studio** API Key.

---

## ⚙️ Setup & Installation

### 1. Database Setup (Supabase)

1.  Create a new project in Supabase.
2.  Go to the **SQL Editor** in your Supabase dashboard.
3.  Run the following SQL script to create the necessary tables and relationships:

```sql
-- 1. Create Sessions Table
CREATE TABLE IF NOT EXISTS sessions (
    session_id UUID PRIMARY KEY,
    title TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Create Chat History Table
CREATE TABLE IF NOT EXISTS chat_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2. Environment Variables

Create a file named `.env` in the root directory of the project and add your credentials:

```ini
SUPABASE_URL="https://your-project-id.supabase.co"
SUPABASE_KEY="your-supabase-anon-key"
GOOGLE_API_KEY="your-google-gemini-api-key"
```

### 3. Run with Docker (Recommended)

The easiest way to run the application is using Docker Compose. This starts both the Backend (FastAPI) and Frontend (Streamlit) automatically.

1.  Open your terminal in the project root.
2.  Run the build command:
    ```bash
    docker-compose up --build
    ```
3.  Wait for the logs to say `Application startup complete`.

---

## 🖥️ Accessing the Application

Once Docker is running, open your web browser:

*   **Chat Interface (Frontend):** [http://localhost:8501](http://localhost:8501)
*   **API Documentation (Backend):** [http://localhost:8000](http://localhost:8000)

> **Note for Windows Users:** If the console says `http://0.0.0.0:8501`, do not click that link directly. Always use **localhost** in your browser.

---

## 📂 Project Structure

```text
llm_chat/
├── backend/
│   ├── main.py          # FastAPI endpoints (Chat, History, Session management)
│   ├── database.py      # Supabase connection & CRUD logic
│   ├── llm_service.py   # Gemini API integration & Streaming logic
│   └── models.py        # Pydantic data models
├── frontend/
│   └── app.py           # Streamlit UI application
├── .env                 # API Keys (Not committed to Git)
├── .dockerignore        # Files excluded from Docker image
├── docker-compose.yml   # Orchestration for Backend + Frontend
├── Dockerfile           # Blueprint for the container image
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## 🐛 Troubleshooting

*   **Docker Error: "The system cannot find the file specified":**
    *   Ensure Docker Desktop is actually running. Open the app and wait for the engine to start.
*   **Database Errors:**
    *   Check your Supabase URL and Key in the `.env` file.
    *   Ensure you ran the SQL setup script exactly as shown above.
*   **Streamlit shows "Connection Error":**
    *   Ensure the backend is running. If using Docker, they communicate automatically. If running manually, ensure FastAPI is running on port 8000.

---
"# llm_chat_app" 
