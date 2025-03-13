import pytest
from unittest.mock import patch
from app import create_app
from bson import ObjectId
from flask_login import login_user
from app.models import Profile


@pytest.fixture
def test_app():
    app = create_app()
    app.config['TESTING'] = True
    yield app


@pytest.fixture
def test_client(test_app):
    return test_app.test_client()


@pytest.fixture
def test_user():
    return Profile({
        '_id': ObjectId('5f0e3d4c5b3f3b3c0e0d6d4f'),
        'email': 'test@khantivong.gov',
        'username': 'test',
        'password': 'password'
    })


@patch('app.auth.users.find_one')
@patch('app.auth.users.insert_one')
def test_signup(mock_users, test_client):
    mock_users.find_one.return_value = None
    mock_users.insert_one.return_value = None
    test_signup = {
        'email': 'art@test.gov',
        'username': 'art',
        'password': 'password'
    }
    response = test_client.post('/signup', json=test_signup)
    assert response.status_code == 201
    assert response.json == {'message': 'Account created!'}
    mock_users.find_one.assert_called_once_with({
        'email': 'art@test.gov'
    })
    mock_users.insert_one.assert_called_once()


@patch('app.auth.users')
def test_signup_existing_user(test_client, mock_users):

    mock_users.find_one.return_value = {
        'email': 'alreadyexists@doj.gov'
    }
    test_signup = {
        'email': 'alreadyexists@doj.gov',
        'username': 'alreadyexists',
        'password': 'password'
    }

    response = test_client.post('/signup', json=test_signup)
    assert response.status_code == 400
    mock_users.find_one.assert_called_once_with({
        'email': 'alreadyexists@doj.gov'
    })
    mock_users.insert_one.assert_not_called()

@patch('app.auth.users.find_one')
@patch('app.auth.bcrypt.generate_password_hash')
@patch('app.auth.login_user')
def test_login(mock_users, mock_bcrypt, test_client, test_user):
    mock_users.find_one.return_value = test_user
    mock_bcrypt.check_password_hash.return_value = True
    test_login = {
        'email': 'test@khantivong.gov',
        'password': 'password'
    }

    response = test_client.post('/login', json=test_login)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == 'Success!'
    assert json_data['user']['id'] == '5f0e3d4c5b3f3b3c0e0d6d4f'
    assert json_data['user']['email'] == test_user['email']
    mock_users.find_one.assert_called_once_with({
        'email': 'test@khantivong.gov'
    })
    mock_bcrypt.check_password_hash.assert_called_once_with('hashed_password', 'password')

@patch('app.auth.users.find_one')
@patch('app.auth.bcrypt.check_password_hash')
@patch('app.auth.login_user')
def test_login_invalid_user(mock_users, mock_bcrypt, test_client):
    mock_users.find_one.return_value = None
    mock_bcrypt.check_password_hash.return_value = False
    test_login = {
        'email': 'invalid@topsecret.co.jp',
        'password': 'password'
    }

    response = test_client.post('/login', json=test_login)
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data['error'] == ('Invalid email or password! Please try again,'
                                  ' or if you meant to sign up, please sign up instead!.')
    mock_users.find_one.assert_called_once_with({
        'email': 'invalid@topsecret.co.jp'
    })

@patch('app.auth.logout_user')
def test_logout(mock_logout_user, test_client):
    response = test_client.get('/logout')
    assert response.status_code == 200
    mock_logout_user.assert_called_once()