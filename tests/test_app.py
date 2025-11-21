"""
Tests for Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    yield
    
    # Reset after test
    activities.clear()
    for key, value in original.items():
        activities[key] = {
            "description": value["description"],
            "schedule": value["schedule"],
            "max_participants": value["max_participants"],
            "participants": value["participants"].copy()
        }


def test_get_activities(client, reset_activities):
    """Test retrieving all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_signup_success(client, reset_activities):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Chess%20Club/signup?email=alex@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert "alex@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_activity_not_found(client, reset_activities):
    """Test signup for non-existent activity"""
    response = client.post(
        "/activities/Nonexistent%20Club/signup?email=alex@mergington.edu"
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_already_signed_up(client, reset_activities):
    """Test signing up for activity when already registered"""
    response = client.post(
        "/activities/Chess%20Club/signup?email=michael@mergington.edu"
    )
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_activity_full(client, reset_activities):
    """Test signing up for a full activity"""
    # Create a full activity
    activities["Test Club"] = {
        "description": "Test",
        "schedule": "Test time",
        "max_participants": 1,
        "participants": ["existing@mergington.edu"]
    }
    
    response = client.post(
        "/activities/Test%20Club/signup?email=new@mergington.edu"
    )
    assert response.status_code == 400
    assert "Activity is full" in response.json()["detail"]


def test_unregister_success(client, reset_activities):
    """Test successful unregistration from activity"""
    response = client.post(
        "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_activity_not_found(client, reset_activities):
    """Test unregister from non-existent activity"""
    response = client.post(
        "/activities/Nonexistent%20Club/unregister?email=alex@mergington.edu"
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_not_signed_up(client, reset_activities):
    """Test unregistering when not signed up"""
    response = client.post(
        "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
    )
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]


def test_signup_then_unregister(client, reset_activities):
    """Test signing up and then unregistering"""
    # Sign up
    response = client.post(
        "/activities/Chess%20Club/signup?email=alex@mergington.edu"
    )
    assert response.status_code == 200
    assert "alex@mergington.edu" in activities["Chess Club"]["participants"]
    
    # Unregister
    response = client.post(
        "/activities/Chess%20Club/unregister?email=alex@mergington.edu"
    )
    assert response.status_code == 200
    assert "alex@mergington.edu" not in activities["Chess Club"]["participants"]
