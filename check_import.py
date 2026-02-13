import sys
import os

print(f"Current working directory: {os.getcwd()}")
print(f"sys.path before modification: {sys.path}")

# Attempt to add src to sys.path
sys.path.insert(0, os.path.abspath('src'))
print(f"sys.path after adding src: {sys.path}")

try:
    import src.domain_document.application.service.document_service
    print("Successfully imported src.domain_document.application.service.document_service")
except ImportError as e:
    print(f"Failed to import src: {e}")

try:
    import src.project_convention.application.service.convention_service
    print("Successfully imported src.project_convention.application.service.convention_service")
except ImportError as e:
    print(f"Failed to import src: {e}")
