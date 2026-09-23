# ResearchAI

ResearchAI is a multi-chat research assistant. You type a question, and it answers with Gemini, using your uploaded notes when they are relevant and calling tools such as the current time or a calculator when the question needs them. Uploaded `.txt` and `.md` files are split, embedded, and stored so later questions can retrieve the matching passages before the model replies.

There are no user accounts. Uploaded files go into one shared knowledge base.

## Features

- Multiple chats, stored in SQLite and restored in the browser
- Markdown replies
- `.txt` and `.md` upload, including drag and drop, up to 2 MB
- Retrieval over uploaded notes with Chroma
- Tools: current Pacific time, and add / subtract / multiply / divide
- A LangGraph workflow that retrieves context, calls tools, and stops after 5 tool rounds

## Architecture

The page is a Django app. Chat and upload requests stay in `views.py`. The live answer path is `chat/langchain_backend`. `chat/manual_backend` is the earlier handwritten version of the same steps and is not used by the page.

```text
Browser
  → chat page, /chat/, /upload/
  → views.py
       ├─ upload: save file → ingest_document()
       │     load → split → embed → Chroma
       └─ chat: load history → generate_response()
             → LangGraph
                  START → retrieve → model
                  model → tools → model   (only if the model requested a tool)
                  model → END              (when there is no tool call)
```

`retrieve` runs once and adds the question plus matching chunks to the message list. `model` calls Gemini. If that reply requests a tool, `tools` runs it and the graph returns to `model`. The loop stops when the model answers in text, or after 5 tool rounds.

## Project layout

```text
.env.example                  # environment variable template; copy to .env
.gitignore                    # ignores .env, the database, uploads, and Chroma data
manage.py                     # Django command entry point
Procfile                      # production start command for Railway
requirements.txt              # pinned Python dependencies

config/                       # Django project package
├── settings.py               # settings, API keys, Chroma path, upload limit
├── urls.py                   # mounts the chat app at /
├── wsgi.py                   # production WSGI entry used by gunicorn
├── asgi.py                   # ASGI entry; not used by the current server
├── templates/chat.html       # chat page markup
└── static/
    ├── css/chat.css          # page styles
    └── js/
        ├── chat.js           # page behavior, including drag and drop
        ├── api.js            # /chat/ and /upload/ requests
        ├── state.js          # chat list saved in the browser
        └── markdown.js       # render assistant markdown

chat/                         # the application
├── views.py                  # page, chat API, and upload API
├── urls.py                   # /, /chat/, and /upload/ routes
├── models.py                 # Conversation and Message tables
├── admin.py                  # registers models in the Django admin
├── apps.py                   # Django app config
├── file_upload.py            # checks and saves an uploaded file
├── migrations/               # database schema changes
├── langchain_backend/        # live answer and ingestion path
│   ├── services.py           # LangGraph and generate_response()
│   ├── nodes.py              # retrieve, model, and tool nodes
│   ├── tools.py              # current time and calculator
│   ├── rag.py                # search existing Chroma data
│   └── ingestion.py          # load, split, embed, and store a file
└── manual_backend/           # earlier handwritten version, not used by the page
    ├── services.py           # handwritten agent loop and generate_response()
    ├── tools.py              # current time and calculator declarations
    ├── document_loader.py    # read and split a .txt or .md file
    ├── embeddings.py         # turn text into Gemini vectors
    ├── vector_store.py       # save chunk vectors in Chroma
    ├── retrieval.py          # search Chroma and filter by distance
    └── ingestion.py          # load, split, embed, and store a file

doc/example/                  # sample notes for trying retrieval
├── sample_research_notes.txt # plain-text sample
└── sample_research_notes.md  # Markdown sample
```

## Quick start

Requires Python 3.13.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Put your Gemini API key in `.env`, then:

```powershell
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/

Sample notes are in `doc/example/`. You can also upload a `.txt` or `.md` file from the composer.

## Configuration

Copy `.env.example` to `.env`. Do not commit `.env`.

| Variable | Purpose |
| --- | --- |
| `GEMINI_API_KEY` | Required. Gemini chat and embeddings |
| `GEMINI_MODEL` | Chat model. Default `gemini-3.7-flash` |
| `GEMINI_EMBEDDING_MODEL` | Embedding model. Default `gemini-embedding-001` |
| `DJANGO_SECRET_KEY` | Django secret |
| `DJANGO_DEBUG` | `True` locally |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hosts |

Uploaded files are stored in `media/`. Vectors are stored in `chroma_data/`. Chat history is stored in `db.sqlite3`. Those paths are local and are listed in `.gitignore`.

## API

`POST /chat/`

```json
{ "message": "What is the research code name?", "conversation_id": 1 }
```

`conversation_id` is optional. The response is `{ "message": "...", "conversation_id": 1 }`.

`POST /upload/` with a multipart file field named `file`. Only `.txt` and `.md` are accepted.

## Deployment

`Procfile` migrates, collects static files, and starts gunicorn. Set `GEMINI_API_KEY` and `DJANGO_SECRET_KEY` in the host's environment. On Railway, `RAILWAY_PUBLIC_DOMAIN` is added to `ALLOWED_HOSTS` and CSRF trusted origins.

Keep a spend limit on the Gemini key if the site is public. The chat API is open: there is no login.
