#!/usr/bin/env python3
"""
Batch script to generate embeddings for existing domain documents and project conventions.

This script iterates through all existing documents and conventions that don't have
embeddings yet and generates them using the EmbeddingService.
"""

import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tqdm import tqdm
from src.container import Container

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_embeddings_for_documents(container: Container):
    """Generate embeddings for all domain documents without embeddings."""
    document_repo = container.document_repository()
    embedding_service = container.embedding_service()

    logger.info("=" * 80)
    logger.info("Generating embeddings for domain documents...")
    logger.info("=" * 80)

    # Get all unique project names
    project_names = document_repo.get_all_unique_project_names()
    logger.info(f"Found {len(project_names)} projects")

    total_processed = 0
    total_success = 0
    total_failed = 0
    total_skipped = 0

    for project_name in project_names:
        logger.info(f"\nProcessing project: {project_name}")

        # Get all documents for this project
        documents = document_repo.find_all_by_project(project_name)
        logger.info(f"Found {len(documents)} documents in {project_name}")

        # Process each document with progress bar
        for doc in tqdm(documents, desc=f"Documents in {project_name}"):
            total_processed += 1

            # Check if embedding already exists (by checking if it's None in the entity)
            # Since we don't have direct access to the embedding field in the domain model,
            # we'll try to generate it and let the repository handle duplicates
            try:
                embedding_service.create_embedding_for_document(doc)
                total_success += 1
                logger.debug(f"Created embedding for document: {doc.identifier}")
            except Exception as e:
                total_failed += 1
                logger.error(f"Failed to create embedding for document {doc.identifier}: {e}")

    logger.info("\n" + "=" * 80)
    logger.info("Domain Documents Summary:")
    logger.info(f"  Total processed: {total_processed}")
    logger.info(f"  Successfully created: {total_success}")
    logger.info(f"  Failed: {total_failed}")
    logger.info(f"  Skipped: {total_skipped}")
    logger.info("=" * 80)

    return total_processed, total_success, total_failed


def generate_embeddings_for_conventions(container: Container):
    """Generate embeddings for all project conventions without embeddings."""
    convention_repo = container.convention_repository()
    embedding_service = container.embedding_service()

    logger.info("\n" + "=" * 80)
    logger.info("Generating embeddings for project conventions...")
    logger.info("=" * 80)

    # Get all unique project names
    project_names = convention_repo.get_all_unique_project_names()
    logger.info(f"Found {len(project_names)} projects")

    total_processed = 0
    total_success = 0
    total_failed = 0
    total_skipped = 0

    for project_name in project_names:
        logger.info(f"\nProcessing project: {project_name}")

        # Get all latest conventions for this project
        conventions = convention_repo.find_all_latest_by_project(project_name)
        logger.info(f"Found {len(conventions)} conventions in {project_name}")

        # Process each convention with progress bar
        for conv in tqdm(conventions, desc=f"Conventions in {project_name}"):
            total_processed += 1

            try:
                embedding_service.create_embedding_for_convention(conv)
                total_success += 1
                logger.debug(f"Created embedding for convention: {conv.identifier}")
            except Exception as e:
                total_failed += 1
                logger.error(f"Failed to create embedding for convention {conv.identifier}: {e}")

    logger.info("\n" + "=" * 80)
    logger.info("Project Conventions Summary:")
    logger.info(f"  Total processed: {total_processed}")
    logger.info(f"  Successfully created: {total_success}")
    logger.info(f"  Failed: {total_failed}")
    logger.info(f"  Skipped: {total_skipped}")
    logger.info("=" * 80)

    return total_processed, total_success, total_failed


def main():
    """Main entry point for the batch embedding generation script."""
    logger.info("Starting batch embedding generation...")
    logger.info(f"Project root: {project_root}")

    try:
        # Initialize container
        container = Container()

        # Generate embeddings for documents
        doc_processed, doc_success, doc_failed = generate_embeddings_for_documents(container)

        # Generate embeddings for conventions
        conv_processed, conv_success, conv_failed = generate_embeddings_for_conventions(container)

        # Final summary
        logger.info("\n" + "=" * 80)
        logger.info("FINAL SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Domain Documents:")
        logger.info(f"  Processed: {doc_processed}, Success: {doc_success}, Failed: {doc_failed}")
        logger.info(f"Project Conventions:")
        logger.info(f"  Processed: {conv_processed}, Success: {conv_success}, Failed: {conv_failed}")
        logger.info(f"Total:")
        logger.info(f"  Processed: {doc_processed + conv_processed}")
        logger.info(f"  Success: {doc_success + conv_success}")
        logger.info(f"  Failed: {doc_failed + conv_failed}")
        logger.info("=" * 80)

        if doc_failed + conv_failed > 0:
            logger.warning(f"Completed with {doc_failed + conv_failed} failures. Check logs for details.")
            return 1
        else:
            logger.info("All embeddings generated successfully!")
            return 0

    except Exception as e:
        logger.error(f"Fatal error during batch processing: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
