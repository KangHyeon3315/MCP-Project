from dependency_injector import containers, providers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain_document.application.service.document_service import DocumentService
from src.domain_document.adapter.output.persistence.repository import DocumentRepository

from src.project_convention.application.service.convention_service import ConventionService
from src.project_convention.adapter.output.persistence.repository import ConventionRepository


class Container(containers.DeclarativeContainer):
    """
    The main dependency injection container for the application.
    """
    wiring_config = containers.WiringConfiguration(
        modules=[
            # Add modules here that need dependency injection
            # e.g., 'src.web.router'
        ]
    )

    # --- Configuration ---
    config = providers.Configuration()
    config.db_url.from_value("postgresql://user:password@localhost:5432/dcma_db")

    # --- Database ---
    db_engine = providers.Singleton(create_engine, url=config.db_url)
    db_session_factory = providers.Factory(sessionmaker, bind=db_engine, autocommit=False, autoflush=False)
    db_session = providers.Resource(db_session_factory)

from dependency_injector import containers, providers

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv # Import load_dotenv

import os # Import os



from src.domain_document.application.service.document_service import DocumentService

from src.domain_document.adapter.output.persistence.repository import DocumentRepository



from src.project_convention.application.service.convention_service import ConventionService

from src.project_convention.adapter.output.persistence.repository import ConventionRepository



load_dotenv() # Explicitly load .env variables at the top



def get_db_session(session_factory: sessionmaker):

    """

    Generator function to provide a database session.

    It ensures that the session is closed after use.

    """

    session = session_factory()

    try:

        yield session

    finally:

        session.close()





class Container(containers.DeclarativeContainer):

    """

    The main dependency injection container for the application.

    """

    wiring_config = containers.WiringConfiguration(

        modules=[

            'src.web.router',

        ]

    )



    # --- Database Configuration from Environment ---

    db_user = os.environ.get("DB_USER", "user")

    db_password = os.environ.get("DB_PASSWORD", "password")

    db_host = os.environ.get("DB_HOST", "localhost")

    db_port = os.environ.get("DB_PORT", "5432")

    db_name = os.environ.get("DB_NAME", "dcma_db")



    # --- Database ---

    db_engine = providers.Singleton(

        create_engine,

        url=f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    )

    db_session_factory = providers.Factory(sessionmaker, bind=db_engine, autocommit=False, autoflush=False)

    

    # Use a Resource with a generator for proper session management

    db_session = providers.Resource(

        get_db_session,

        session_factory=db_session_factory

    )



    # --- Domain Document Module ---

    document_repository = providers.Factory(

        DocumentRepository,

        session=db_session,

    )

    document_service = providers.Factory(

        DocumentService,

        document_repository=document_repository,

    )



    # --- Project Convention Module ---

    convention_repository = providers.Factory(

        ConventionRepository,

        session=db_session,

    )

    convention_service = providers.Factory(

        ConventionService,

        convention_repository=convention_repository,

    )




    # --- Project Convention Module ---
    convention_repository = providers.Factory(
        ConventionRepository,
        session=db_session,
    )
    convention_service = providers.Factory(
        ConventionService,
        convention_repository=convention_repository,
    )
