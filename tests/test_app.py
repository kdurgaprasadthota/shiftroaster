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
        'password': 'admin111'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome, admin' in response.data

def test_unauthenticated_redirect(client):
    """Test that protected routes redirect to login."""
    response = client.get('/roaster', follow_redirects=True)
    assert b'Login' in response.data
