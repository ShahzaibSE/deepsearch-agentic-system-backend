from agents import set_tracing_disabled
import asyncio
from app.server import Server
from fastapi import FastAPI
from app.routes import create_main_router
from pathlib import Path

set_tracing_disabled(disabled=True)

def main():
    print("Hello from deepsearch!")
    
    # Create FastAPI app
    app = FastAPI(title="DeepSearch API", version="1.0.0")
    
    # Use your factory function to get the main router with all discovered routes
    main_router = create_main_router()
    app.include_router(main_router)
    
    # Create and run server
    server = Server(app=app)
    server.run()

if __name__ == "__main__":
    asyncio.run(main())
