import logging
import traceback
from functools import wraps

from flask import jsonify

# Configure logging
logging.basicConfig(
    level=logging.ERROR, 
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as ve:
            return jsonify({"error": "Validation error", "message": str(ve)}), 400
        except KeyError as ke:
            return jsonify({"error": "Missing key", "message": str(ke)}), 400
        except TypeError as te:
            return jsonify({"error": "Type error", "message": str(te)}), 400
        except Exception as e:
            # Log the full traceback for debugging purposes
            logging.error(f"Exception occurred: {e}")
            logging.error(traceback.format_exc())
            return jsonify({"error": "Internal error", "message": "An unexpected error occurred"}), 500
    return wrapper
