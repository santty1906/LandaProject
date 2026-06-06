# LANDA Architecture Overview

## Stack

- **Backend**: Flask + SQLAlchemy + SQLite
- **Frontend**: Bootstrap 5 + Vanilla JavaScript (server-rendered Jinja2 templates)
- **Auth**: Session-based with bcrypt password hashing
- **Face Recognition**: DeepFace (Facenet512) — optional biometric login
- **PWA**: Manifest + Service Worker for installable mobile experience

## Architecture Decisions

| Decision | Rationale |
|---|---|
| Monolithic Flask app | Simple to develop, test, and deploy |
| SQLite (no PostgreSQL) | Zero setup, file-based, perfect for prototyping |
| Session-based auth | Simpler than JWT for server-rendered apps |
| Server-rendered HTML | No CORS, no separate API server needed |
| Vanilla JS + Bootstrap 5 | No build step, no npm, immediate iteration |
| DeepFace pretrained models | State-of-the-art face recognition without training |

## Folder Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── app.py               # Flask app factory
│   ├── config.py             # Configuration loading
│   ├── models.py             # SQLAlchemy models (User, AuditLog)
│   ├── auth.py               # Login / register / logout routes
│   ├── routes.py             # Dashboard / settings / face API routes
│   ├── security.py           # Password hashing + login_required decorator
│   ├── face_service.py       # DeepFace enrollment and verification
│   ├── templates/            # Jinja2 templates
│   │   ├── layout.html       # Base layout with bottom nav
│   │   ├── login.html        # Login screen
│   │   ├── register.html     # Registration screen
│   │   ├── dashboard.html    # Banking dashboard
│   │   └── settings.html     # Settings + Face ID enrollment
│   └── static/
│       ├── css/base.css      # Mobile-first banking styles
│       ├── js/app.js         # Camera capture + Face ID logic
│       ├── manifest.json     # PWA manifest
│       ├── service-worker.js # Offline caching
│       └── icons/            # PWA app icons
├── tests/
│   ├── conftest.py           # Pytest fixtures (app, client, user)
│   ├── test_auth.py          # Registration + login + logout tests
│   ├── test_routes.py        # Protected routes + face API tests
│   ├── test_security.py      # Password hashing unit tests
│   └── test_face.py          # Face service edge case tests
├── instance/                 # SQLite DB + face embeddings (gitignored)
├── run.py                    # Entry point
├── requirements.txt
├── pytest.ini
├── .env
└── .env.example
```

## Request Flow

```
Browser                      Flask
  │                            │
  ├── GET /login ──────────────┤  render_template('login.html')
  ├── POST /auth/login ────────┤  validate → set session → redirect
  ├── GET /dashboard ──────────┤  login_required → render dashboard
  ├── POST /api/face/enroll ───┤  save embeddings → update user
  └── GET /logout ─────────────┤  clear session → redirect
```

## Authentication Flow

1. User registers with username, email, password
2. Password is hashed with `werkzeug.security.generate_password_hash`
3. On login, password is verified against stored hash
4. On success, `user_id` and `username` are stored in Flask session
5. Protected routes check `user_id` in session via `@login_required`
6. All auth events are logged to `AuditLog`

## Facial Recognition Workflow

1. User clicks "Enroll Face" in Settings
2. Camera captures 3 angles: frontal, left, right
3. DeepFace extracts 512-dimensional embeddings for each
4. Embeddings are saved to `instance/faces/{username}/embeddings.pkl`
5. During login, camera captures a single frame
6. DeepFace extracts embedding, compares to enrolled (Euclidean distance)
7. Match if distance < threshold (default 0.35)
8. Password login always available as fallback

## Security Considerations

- Passwords hashed with bcrypt (via Werkzeug)
- Flask session uses signed cookies (SECRET_KEY)
- Face embeddings stored locally — no cloud transmission
- Face images deleted immediately after embedding extraction
- SQLite database in `instance/` (gitignored)
- Audit log tracks all auth events
- Rate limiting recommended before production
