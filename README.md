# Google Auth Demo Application

This is a demo application that demonstrates Google OAuth2 authentication with a FastAPI backend and React frontend.

## Features

- Google OAuth2 login
- User session management
- Protected routes
- PostgreSQL database storage

## Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL database
- Google Cloud Project with OAuth2 credentials

## Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example` and fill in your credentials:
   ```
   cp .env.example .env
   ```

5. Update the `.env` file with your Google OAuth2 credentials and database URL.

6. Run the backend server:
   ```
   python run.py
   ```

## Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install the required packages:
   ```
   npm install
   ```

3. Run the development server:
   ```
   npm run dev
   ```

## Google OAuth2 Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API
4. Create OAuth2 credentials (Client ID and Client Secret)
5. Add `http://localhost:8000/auth/callback` to the authorized redirect URIs
6. Update the `.env` file with your Google OAuth2 credentials

## Database Setup

1. Create a PostgreSQL database
2. Update the `DATABASE_URL` in your `.env` file with your database connection string
3. The application will automatically create the necessary tables on startup

## Usage

1. Start the backend server
2. Start the frontend development server
3. Navigate to `http://localhost:5173` in your browser
4. Click the "Sign in with Google" button
5. Complete the Google authentication flow
6. You should be redirected back to the application and see your user information

## Project Structure

```
.
├── backend/
│   ├── main.py          # Main FastAPI application
│   ├── config.py        # Configuration settings
│   ├── database.py      # Database setup
│   ├── models.py        # Database models
│   ├── schemas.py       # Pydantic schemas
│   ├── auth_utils.py    # Authentication utilities
│   ├── routers/
│   │   └── auth.py      # Authentication routes
│   ├── requirements.txt # Python dependencies
│   ├── .env.example     # Environment variables template
│   └── run.py           # Application entry point
└── frontend/
    ├── src/
    │   ├── App.jsx      # Main application component
    │   ├── Callback.jsx # Google OAuth2 callback handler
    │   └── main.jsx     # Application entry point
    └── package.json     # Node.js dependencies
```

## API Endpoints

- `GET /auth/login` - Initiate Google OAuth2 login
- `GET /auth/callback` - Handle Google OAuth2 callback
- `POST /auth/logout` - Logout user
- `GET /auth/user` - Get current user info (not fully implemented)

## License

This project is licensed under the MIT License.
