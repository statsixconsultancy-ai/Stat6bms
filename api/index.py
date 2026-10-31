import os
import sys

# Ensure project root is on sys.path for Vercel Python serverless functions
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.services.gateway.main import app
