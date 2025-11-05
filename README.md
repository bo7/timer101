# Zeit Erfassung - Time Tracking System

A modern time tracking system for field employees with separate frontend and backend.

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy 2.0** - ORM with full typing support
- **SQLite** - Database (with PostgreSQL migration path)
- **Pydantic** - Data validation
- **JWT** - Authentication

### Frontend
- **Next.js 15.5** - React framework with App Router
- **Tailwind CSS v4** - Utility-first CSS framework
- **TypeScript** - Type safety
- **React Hook Form** - Form management

## Project Structure

```
timer101/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── models/    # SQLAlchemy models
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── routers/   # API endpoints
│   │   ├── core/      # Config, security, database
│   │   └── main.py    # FastAPI app
│   ├── tests/
│   └── requirements.txt
├── frontend/          # Next.js frontend
│   ├── src/
│   │   ├── app/       # Next.js App Router
│   │   ├── components/# React components
│   │   └── lib/       # Utilities
│   └── package.json
└── DATABASE_SCHEMA.md # Database documentation
```

## Features

### Employee Frontend
- **Login** - Secure authentication with username/password
- **Add Today** - Quick time entry for current day
  - AJAX customer search
  - Dynamic location dropdown based on customer
  - Multiple entries per day
  - Unsaved changes warning
- **Add Other Day** - Time entry for any date
- **Show Day** - View and edit entries
  - Processed entries are read-only
  - Non-processed entries are editable

### Admin Features (Future)
- Mark entries as processed
- User management
- Reports and exports

## Database Schema

See [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) for complete schema documentation.

### Key Tables
- **users** - Employee accounts with admin flag
- **customers** - Client information
- **locations** - Work locations per customer
- **worktimes** - Time tracking entries

## Getting Started

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs on: http://localhost:8000
API docs: http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on: http://localhost:3000

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user

### Customers
- `GET /api/customers` - List all active customers
- `GET /api/customers/search?q=` - Search customers (AJAX)

### Locations
- `GET /api/locations?customer_id=` - Get locations for customer

### Worktimes
- `GET /api/worktimes?date=` - Get worktimes for date
- `POST /api/worktimes` - Create worktime entry
- `PUT /api/worktimes/{id}` - Update worktime entry
- `DELETE /api/worktimes/{id}` - Delete worktime entry

### Admin
- `PUT /api/admin/worktimes/{id}/process` - Mark entry as processed
- `GET /api/admin/users` - List all users

## Development

### Backend
- Uses SQLAlchemy 2.0 with async support
- JWT-based authentication
- CORS enabled for frontend
- Automatic API documentation with Swagger UI

### Frontend
- Next.js App Router (server and client components)
- Tailwind CSS v4 for styling
- Client-side state management
- Form validation with React Hook Form

## Migration to PostgreSQL

When ready to migrate from SQLite to PostgreSQL:

1. Update database connection in `backend/app/core/config.py`
2. Install psycopg2: `pip install psycopg2-binary`
3. Run migrations with Alembic
4. Update any SQLite-specific queries

See DATABASE_SCHEMA.md for detailed migration notes.

## Security

- Passwords hashed with bcrypt
- JWT tokens with expiration
- CORS configured for production
- SQL injection protection via SQLAlchemy ORM
- XSS protection via React
- CSRF tokens for state-changing operations

## License

MIT
