import os

from uorg import application
from uorg.utils.logging import setup_logging

if __name__ == "__main__":
    # Get the port defined in env if defined, otherwise sets it to 5000
    port = int(os.environ.get("FLASK_PORT", "5000"))
    # Default debug is true
    debug = bool(os.environ.get("FLASK_DEBUG", False))

    setup_logging()

    # Runs the main loop
    application.run(host=os.getenv("FLASK_HOST", "0.0.0.0"), port=port, debug=debug)
