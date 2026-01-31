from fastapi import FastAPI
from src.container import Container
# We will create this router file in the next step
from src.web import router 

def create_app() -> FastAPI:
    """
    Creates the FastAPI application, initializes the container, and includes the routers.
    """
    container = Container()
    
    # Wire the container to the modules that need injection
    container.wire(modules=[router])
    
    app = FastAPI()
    app.container = container
    
    # Include the API router
    app.include_router(router.router)
    
    @app.get("/")
    def read_root():
        return {"message": "DCMA (Domain & Convention Management Agent) API is running."}
        
    return app

app = create_app()
