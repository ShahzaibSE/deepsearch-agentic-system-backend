from fastapi import APIRouter
from pathlib import Path
import os
import importlib


def create_main_router():
    """
    Create the main router for the application.
    """
    router = APIRouter()
    file_paths = Path(__file__).parent.glob('*.py')
    for file_path in file_paths:
        if file_path.name == '__init__.py' or file_path.name.startswith('_'):
            continue

        print(f"Found route file: {file_path.name}")  # Debug info

        try:
            # Get the module name from the file path
            module_name = file_path.stem
            # Import the module
            module = importlib.import_module(module_name, package='app.routes')
            # Get the router from the module
            if hasattr(module, 'router'):
                router.include_router(module.router)
                print(f"Registered router from {module_name}")
            else:
                print(f"No router found in {module_name}")
        except ImportError as e   :
            print(f"Error importing {module_name}: {e}")
            continue
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
    
    return router