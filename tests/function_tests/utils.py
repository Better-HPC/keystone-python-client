import os

API_HOST = os.environ.get('TEST_API_HOST', 'http://localhost:8000')
API_USER = os.environ.get('TEST_API_USER', 'admin')
API_PASSWORD = os.environ.get('TEST_API_PASSWORD', 'quickstart')
