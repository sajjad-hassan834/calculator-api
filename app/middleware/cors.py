from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import settings


def setup_cors(app: FastAPI) -> None:
    origins = settings.cors_origins
    if isinstance(origins, str):
        origins = [origins]
        
    # Ensure Vercel domains are always allowed, bypassing any .env ["*"] overrides
    required_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "https://calculator-adminapp.vercel.app",
        "https://calculator-app-chi-five.vercel.app"
    ]
    
    # If wildcard is found, fallback to echoing origin via regex or just use required
    if "*" in origins or '["*"]' in origins:
        origins = required_origins
    else:
        for r in required_origins:
            if r not in origins:
                origins.append(r)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
