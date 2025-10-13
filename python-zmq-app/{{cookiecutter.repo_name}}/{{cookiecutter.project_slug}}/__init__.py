import logging
import sys


# Configure logging for the {{cookiecutter.project_slug}} package
def setup_logging(level=logging.INFO):
    """Setup logging configuration for {{cookiecutter.project_slug}}"""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


# Setup default logging
setup_logging()
