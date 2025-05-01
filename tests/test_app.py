import pytest
from app import app, db, User, Activity

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_register_login_logout(client):
    # Register user
    rv = client.post('/register', data={
        'name': 'Test User',
        'email': 'testuser@rvu.edu.in',
        'password': 'password123',
        'role': 'student',
        'usn': '1RVU23CSE140'
    }, follow_redirects=True)
    assert b'Registration successful' in rv.data

    # Login user
    rv = client.post('/login', data={
        'email': 'testuser@rvu.edu.in',
        'password': 'password123'
    }, follow_redirects=True)
    assert b'Logout' in rv.data or b'logged in' in rv.data

    # Logout user
    rv = client.get('/logout', follow_redirects=True)
    assert b'You have been logged out' in rv.data

def test_invalid_registration(client):
    # Invalid email domain
    rv = client.post('/register', data={
        'name': 'Invalid Email',
        'email': 'invalid@example.com',
        'password': 'password123',
        'role': 'student',
        'usn': '1RVU23CSE140'
    }, follow_redirects=True)
    assert b'Only @rvu.edu.in emails are allowed' in rv.data

    # Invalid USN format
    rv = client.post('/register', data={
        'name': 'Invalid USN',
        'email': 'valid@rvu.edu.in',
        'password': 'password123',
        'role': 'student',
        'usn': '12345'
    }, follow_redirects=True)
    assert b'Invalid USN format' in rv.data

def test_helpdesk_qa_endpoint(client):
    rv = client.get('/helpdesk/qa')
    assert rv.status_code == 200
    assert rv.is_json

def test_unauthorized_activity_submission(client):
    rv = client.post('/submit', data={
        'title': 'Test Activity',
        'description': 'Test Description',
        'activity_type': 'journal_q1q2'
    }, follow_redirects=True)
    # Should redirect to login because not logged in
    assert b'login' in rv.data.lower()

# Additional tests for faculty approval, file upload limits, etc. can be added similarly.
