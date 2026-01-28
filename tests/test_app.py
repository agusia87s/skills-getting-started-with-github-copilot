"""
Tests for the Mergington High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application"""
    return TestClient(app)


class TestRootEndpoint:
    """Test cases for the root endpoint"""

    def test_root_redirect(self, client):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestActivitiesEndpoint:
    """Test cases for getting activities"""

    def test_get_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Check that all expected activities are present
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Soccer Team" in data
        assert "Basketball Club" in data
        assert "Art Club" in data
        assert "Drama Society" in data
        assert "Math Olympiad" in data
        assert "Science Club" in data

    def test_activities_have_required_fields(self, client):
        """Test that activities have all required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity in data.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)

    def test_activities_have_correct_structure(self, client):
        """Test that activities have correct data types"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert isinstance(chess_club["description"], str)
        assert isinstance(chess_club["schedule"], str)
        assert isinstance(chess_club["max_participants"], int)
        assert isinstance(chess_club["participants"], list)


class TestSignupEndpoint:
    """Test cases for signing up for activities"""

    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_verify_addition(self, client):
        """Test that signup actually adds student to participants"""
        email = "testuser@mergington.edu"
        client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        
        response = client.get("/activities")
        data = response.json()
        assert email in data["Programming Class"]["participants"]

    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_already_registered(self, client):
        """Test that students can't signup twice"""
        email = "michael@mergington.edu"
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_multiple_activities(self, client):
        """Test that a student can sign up for multiple activities"""
        email = "ambitious@mergington.edu"
        
        # Sign up for first activity
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post(
            "/activities/Art Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify in both activities
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
        assert email in data["Art Club"]["participants"]


class TestUnregisterEndpoint:
    """Test cases for unregistering from activities"""

    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_verify_removal(self, client):
        """Test that unregister actually removes student from participants"""
        email = "daniel@mergington.edu"
        client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]

    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregister from activity that doesn't exist"""
        response = client.delete(
            "/activities/Fake Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_signed_up(self, client):
        """Test that students can't unregister if not signed up"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_signup_after_unregister(self, client):
        """Test that a student can signup again after unregistering"""
        email = "flexible@mergington.edu"
        
        # Sign up
        client.post(
            "/activities/Soccer Team/signup",
            params={"email": email}
        )
        
        # Unregister
        response1 = client.delete(
            "/activities/Soccer Team/unregister",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up again
        response2 = client.post(
            "/activities/Soccer Team/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
