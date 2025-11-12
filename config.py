import os

# Default: if not set, assume backend runs on localhost:5000
API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:5000/api")
