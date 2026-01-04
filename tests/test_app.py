import pytest

def test_login_page(client):
    """Test that the login page loads."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_admin_login(client, admin_user):
    """Test login with admin credentials."""
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome, admin' in response.data

def test_unauthenticated_redirect(client):
    """Test that protected routes redirect to login."""
    response = client.get('/roaster', follow_redirects=True)
    assert b'Login' in response.data

def test_add_member(client, admin_user):
    """Test adding a member with profile fields."""
    client.post('/login', data={'username': 'admin', 'password': 'admin123'})
    response = client.post('/add_member', data={
        'username': 'newuser',
        'password': 'password123',
        'role': 'Member',
        'full_name': 'New User Name',
        'member_id': 'MEM-999',
        'email': 'new@example.com'
    }, follow_redirects=True)
    assert b'Member added successfully' in response.data
    assert b'New User Name' in response.data
    assert b'MEM-999' in response.data
    assert b'new@example.com' in response.data

def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {"status": "healthy"}

def test_metrics_endpoint(client):
    """Test the metrics endpoint."""
    response = client.get('/metrics')
    assert response.status_code == 200
    assert b'app_info' in response.data

def test_edit_member(client, admin_user):
    """Test editing a member's profile fields."""
    client.post('/login', data={'username': 'admin', 'password': 'admin123'})
    # Add first
    client.post('/add_member', data={
        'username': 'edituser',
        'password': 'password123',
        'full_name': 'Initial Name',
        'member_id': 'EDIT-111'
    })
    
    from models import User
    with client.application.app_context():
        user = User.query.filter_by(username='edituser').first()
        user_id = user.id
    
    # Edit
    response = client.post(f'/edit_member/{user_id}', data={
        'username': 'edituser',
        'role': 'Member',
        'full_name': 'Updated Name',
        'member_id': 'EDIT-222'
    }, follow_redirects=True)
    
    assert b'Member updated successfully' in response.data
    assert b'Updated Name' in response.data
    assert b'EDIT-222' in response.data
