# Architecture Overview

## Tech Stack
- **Backend**: FastAPI (Python) + Motor (async MongoDB driver)
- **Database**: MongoDB (via Docker)
- **Auth**: JWT (stateless, via PyJWT + passlib/bcrypt)
- **Frontend**: TBD
- **Containerization**: Docker Compose

## Backend Structure
```
BookWebsite/
├── main.py                    # FastAPI app entry point
├── api/                       # API route handlers (endpoints)
│   ├── auth.py                # /auth/register, /auth/login, get_current_user
│   ├── books.py               # /books/ CRUD + search + featured
│   ├── authors.py             # /authors/ CRUD + search + /books
│   └── readers.py             # /readers/ CRUD + add-book-to-list
├── app/
│   ├── model/                 # Pydantic models (data shapes)
│   │   ├── user.py            # UserCreate, UserInDB, Token
│   │   ├── book.py            # Book (title, author, content, biography, image)
│   │   ├── author.py          # Author (name, bio, book_list, profile_picture, user_id)
│   │   └── readers.py         # Reader (name, favorites, in_progress, finished, user_id)
│   ├── crud/                  # Database operations (MongoDB queries)
│   │   ├── user.py            # create_user, find_user_by_username
│   │   ├── books.py           # CRUD + list_books_alphabetical, get_books_by_ids
│   │   ├── authors.py         # CRUD + get_author_by_user_id, search_authors_by_name
│   │   └── readers.py         # CRUD + get_reader_by_user_id
│   ├── db/
│   │   └── database.py        # MongoDB connection
│   └── auth_utils.py          # Password hashing, JWT encode/decode
├── docs/design/               # Design documentation
├── frontend/                  # Frontend (TBD)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env                       # SECRET_KEY (not in git)
```

## Data Flow
```
Client (Browser)
    │
    ▼
API Layer (api/*.py)          ← Handles HTTP, auth checks, validation
    │
    ▼
CRUD Layer (app/crud/*.py)    ← Talks to MongoDB
    │
    ▼
MongoDB (Docker)              ← Stores all data
```

## Auth Flow
```
Register → hash password → save User + auto-create Reader/Author profiles
Login    → verify password → create JWT with {sub: username, roles: [...]}
Request  → extract JWT from header → decode → verify → inject current_user
```

## Collections in MongoDB
- `users` — login credentials + roles
- `authors` — author profiles (linked to users via user_id)
- `readers` — reader profiles (linked to users via user_id)
- `books` — book data
