import os
import sys
import uvicorn
from app.database import init_db

if __name__ == "__main__":
    print("Initializing Compliance Centras Database...")
    init_db()
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() in ("true", "1")
    workers = int(os.getenv("UVICORN_WORKERS", "1"))

    print(f"Starting Compliance Centras on http://{host}:{port} (workers={workers}, reload={reload}) ...")
    uvicorn.run("app.main:app", host=host, port=port, reload=reload, workers=workers if not reload else 1)
