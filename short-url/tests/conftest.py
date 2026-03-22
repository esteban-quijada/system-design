import os
import sys

# Set env vars before importing the app — these are read at module load time
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_DB", "test")

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../apps/url-shortener"))
