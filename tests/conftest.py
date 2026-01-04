import pytest
from app import app, db
from models import User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def admin_user(client):
    from werkzeug.security import generate_password_hash
    with app.app_context():
        admin = User(username='admin', password_hash=generate_password_hash('admin111'), role='Admin')
        db.session.add(admin)
        db.session.commit()
    return admin
