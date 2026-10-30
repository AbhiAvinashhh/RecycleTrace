"""
RecycleTrace - Pytest Configuration & Test Fixtures
"""
import pytest
import os
import sys
from pymongo import MongoClient

# Ensure app is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from config import TestingConfig
from models.indexes import initialize_collections

@pytest.fixture(scope="session")
def mongo_test_db():
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    db = client["recycletrace_test_suite"]
    yield db
    # Cleanup after test suite
    client.drop_database("recycletrace_test_suite")

@pytest.fixture(scope="function")
def app(mongo_test_db):
    class AppTestConfig(TestingConfig):
        MONGO_URI = "mongodb://localhost:27017/recycletrace_test_suite"
        WTF_CSRF_ENABLED = False
        SECRET_KEY = "test-secret-key-123"

    # Clean collections before each test
    for col in ["users", "waste_batches", "tracking_events", "facilities", "processing_records", "audit_logs"]:
        mongo_test_db[col].delete_many({})

    initialize_collections(mongo_test_db)
    app = create_app(AppTestConfig)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_db(app):
    return app.db

