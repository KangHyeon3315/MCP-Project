from fastapi import FastAPI
from src.container import Container
from src.web import router as api_router
from src.web import ui_router

def create_app() -> FastAPI:
    """
    Creates the FastAPI application, initializes the container, and includes the routers.
    """
    container = Container()

    # Wire the container to the modules that need injection
    container.wire(modules=[api_router, ui_router])

    app = FastAPI()
    app.container = container

    # Include the API and UI routers
    app.include_router(api_router.router)
    app.include_router(ui_router.router)

    @app.get("/health_check")
    def health_check():
        return {"status": "ok"}

    return app

app = create_app()
