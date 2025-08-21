import os
import pytest
from motivation_api.app import app, db
from motivation_api.models import Quote

# Test configuration
ADMIN_API_KEY = "test-admin-key-123"
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['ADMIN_API_KEY'] = ADMIN_API_KEY

@pytest.fixture
def client():
    """Create test client"""
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture
def headers():
    """Return headers with admin API key"""
    return {"x-api-key": ADMIN_API_KEY}