"""
Integration tests for Mergington High School Activity Management API.

These tests use the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the API call being tested
- Assert: Verify response status, structure, and data values
"""

import pytest


# ============================================================================
# GET / - Homepage Redirect Tests
# ============================================================================

class TestHomepage:
    """Tests for the root endpoint that serves the homepage."""

    def test_homepage_redirect_status_code(self, client):
        """
        Verify that GET / returns a redirect response.
        
        Arrange: Test client is ready
        Act: Send GET request to /
        Assert: Response status code indicates redirect (307)
        """
        # Arrange
        expected_status = 307

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == expected_status

    def test_homepage_redirect_location(self, client):
        """
        Verify that GET / redirects to the static index.html file.
        
        Arrange: Test client is ready
        Act: Send GET request to / without following redirects
        Assert: Location header points to /static/index.html
        """
        # Arrange
        expected_redirect_url = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert "location" in response.headers
        assert response.headers["location"] == expected_redirect_url


# ============================================================================
# GET /activities - List All Activities Tests
# ============================================================================

class TestGetActivities:
    """Tests for the endpoint that retrieves all activities."""

    def test_get_activities_status_code(self, client):
        """
        Verify that GET /activities returns a success response.
        
        Arrange: Test client is ready
        Act: Send GET request to /activities
        Assert: Response status code is 200 (OK)
        """
        # Arrange
        expected_status = 200

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == expected_status

    def test_get_activities_returns_dict(self, client):
        """
        Verify that GET /activities returns a JSON object (dict).
        
        Arrange: Test client is ready
        Act: Send GET request to /activities and parse JSON
        Assert: Response body is a dictionary
        """
        # Arrange
        # (no setup needed)

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert isinstance(data, dict)

    def test_get_activities_contains_all_activities(self, client):
        """
        Verify that GET /activities returns all 10 predefined activities.
        
        Arrange: Expected activity names are known
        Act: Send GET request to /activities
        Assert: Response contains all 10 activity names
        """
        # Arrange
        expected_activities = {
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Drama Club",
            "Art Studio",
            "Robotics Club",
            "Debate Team"
        }

        # Act
        response = client.get("/activities")
        data = response.json()
        actual_activities = set(data.keys())

        # Assert
        assert actual_activities == expected_activities

    def test_get_activities_has_required_fields(self, client):
        """
        Verify that each activity has required fields.
        
        Arrange: Expected activity fields are known
        Act: Send GET request to /activities and examine first activity
        Assert: Each activity has description, schedule, max_participants, and participants fields
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        data = response.json()
        first_activity = data["Chess Club"]
        actual_fields = set(first_activity.keys())

        # Assert
        assert required_fields.issubset(actual_fields)

    def test_get_activities_participants_is_list(self, client):
        """
        Verify that participants field contains a list of emails.
        
        Arrange: Test client is ready
        Act: Send GET request to /activities
        Assert: participants field is a list for all activities
        """
        # Arrange
        # (no setup needed)

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list), \
                f"{activity_name} participants should be a list"


# ============================================================================
# POST /activities/{activity_name}/signup - Signup Tests
# ============================================================================

class TestSignupForActivity:
    """Tests for the endpoint that signs up a student for an activity."""

    def test_signup_happy_path(self, client):
        """
        Verify successful signup for an activity with valid activity name and email.
        
        Arrange: Valid activity name (Basketball Team) and student email
        Act: Send POST request to /activities/Basketball Team/signup with email parameter
        Assert: Response status is 200 and confirmation message is returned
        """
        # Arrange
        activity_name = "Basketball Team"
        student_email = "test.student@mergington.edu"
        expected_status = 200

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == expected_status
        assert "message" in response.json()
        assert student_email in response.json()["message"]

    def test_signup_invalid_activity_name(self, client):
        """
        Verify that signup fails with a 404 error for non-existent activity.
        
        Arrange: Non-existent activity name and valid email
        Act: Send POST request with invalid activity name
        Assert: Response status is 404 and error detail indicates activity not found
        """
        # Arrange
        invalid_activity = "Underwater Basket Weaving"
        student_email = "test.student@mergington.edu"
        expected_status = 404

        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == expected_status
        assert "Activity not found" in response.json()["detail"]

    def test_signup_missing_email_parameter(self, client):
        """
        Verify that signup fails when email parameter is missing.
        
        Arrange: Valid activity name but no email parameter
        Act: Send POST request without email query parameter
        Assert: Response status is 422 (validation error)
        """
        # Arrange
        activity_name = "Programming Class"
        expected_status = 422

        # Act
        response = client.post(f"/activities/{activity_name}/signup")

        # Assert
        assert response.status_code == expected_status

    def test_signup_duplicate_email(self, client):
        """
        Verify that signup fails when student is already registered for activity.
        
        Arrange: An activity (Chess Club) that has existing participant (michael@mergington.edu)
        Act: Send POST request to sign up the same email again
        Assert: Response status is 400 and error indicates already signed up
        """
        # Arrange
        activity_name = "Chess Club"
        student_email = "michael@mergington.edu"  # Already in Chess Club participants
        expected_status = 400

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == expected_status
        assert "already signed up" in response.json()["detail"]

    def test_signup_returns_confirmation_message(self, client):
        """
        Verify that successful signup returns a confirmation message with activity and email.
        
        Arrange: Valid activity and email
        Act: Send POST request for signup
        Assert: Response JSON contains confirmation message with both activity name and email
        """
        # Arrange
        activity_name = "Tennis Club"
        student_email = "alice@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        response_data = response.json()

        # Assert
        assert "message" in response_data
        assert activity_name in response_data["message"]
        assert student_email in response_data["message"]


# ============================================================================
# DELETE /activities/{activity_name}/unregister - Unregister Tests
# ============================================================================

class TestUnregisterFromActivity:
    """Tests for the endpoint that unregisters a student from an activity."""

    def test_unregister_happy_path(self, client):
        """
        Verify successful unregister when student is registered for activity.
        
        Arrange: Activity (Chess Club) and student already registered (michael@mergington.edu)
        Act: Send DELETE request to /activities/Chess Club/unregister with email parameter
        Assert: Response status is 200 and confirmation message is returned
        """
        # Arrange
        activity_name = "Chess Club"
        student_email = "michael@mergington.edu"
        expected_status = 200

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == expected_status
        assert "message" in response.json()
        assert student_email in response.json()["message"]

    def test_unregister_invalid_activity_name(self, client):
        """
        Verify that unregister fails with 404 for non-existent activity.
        
        Arrange: Non-existent activity name and valid email
        Act: Send DELETE request with invalid activity name
        Assert: Response status is 404 and error indicates activity not found
        """
        # Arrange
        invalid_activity = "Yodeling Class"
        student_email = "test@mergington.edu"
        expected_status = 404

        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/unregister",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == expected_status
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_missing_email_parameter(self, client):
        """
        Verify that unregister fails when email parameter is missing.
        
        Arrange: Valid activity name but no email parameter
        Act: Send DELETE request without email query parameter
        Assert: Response status is 422 (validation error)
        """
        # Arrange
        activity_name = "Programming Class"
        expected_status = 422

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister")

        # Assert
        assert response.status_code == expected_status

    def test_unregister_student_not_registered(self, client):
        """
        Verify that unregister fails when student is not registered for activity.
        
        Arrange: Activity (Basketball Team) and email that is NOT in participants
        Act: Send DELETE request for student not registered
        Assert: Response status is 400 and error indicates student not signed up
        """
        # Arrange
        activity_name = "Basketball Team"  # Has no participants
        student_email = "unregistered@mergington.edu"
        expected_status = 400

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == expected_status
        assert "not signed up" in response.json()["detail"]

    def test_unregister_returns_confirmation_message(self, client):
        """
        Verify that successful unregister returns a confirmation message.
        
        Arrange: Valid activity and student registered in that activity
        Act: Send DELETE request for unregister
        Assert: Response JSON contains confirmation message with activity and email
        """
        # Arrange
        activity_name = "Programming Class"
        student_email = "emma@mergington.edu"  # Already in Programming Class

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        response_data = response.json()

        # Assert
        assert "message" in response_data
        assert activity_name in response_data["message"]
        assert student_email in response_data["message"]


# ============================================================================
# Integration Tests - Multi-step Scenarios
# ============================================================================

class TestIntegrationScenarios:
    """Tests for complete user workflows involving multiple API calls."""

    def test_signup_then_unregister_workflow(self, client):
        """
        Verify a complete workflow: signup → verify registration → unregister → verify removal.
        
        Arrange: New student, empty activity (Tennis Club)
        Act: Sign up → get activities to verify participant added → unregister → verify participant removed
        Assert: Participant count changes correctly at each step
        """
        # Arrange
        activity_name = "Tennis Club"
        new_student = "workflow@mergington.edu"

        # Act & Assert - Step 1: Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()[activity_name]["participants"])

        # Act & Assert - Step 2: Sign up the student
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_student}
        )
        assert signup_response.status_code == 200

        # Act & Assert - Step 3: Verify student was added
        response = client.get("/activities")
        after_signup_count = len(response.json()[activity_name]["participants"])
        assert after_signup_count == initial_count + 1
        assert new_student in response.json()[activity_name]["participants"]

        # Act & Assert - Step 4: Unregister the student
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": new_student}
        )
        assert unregister_response.status_code == 200

        # Act & Assert - Step 5: Verify student was removed
        response = client.get("/activities")
        after_unregister_count = len(response.json()[activity_name]["participants"])
        assert after_unregister_count == initial_count
        assert new_student not in response.json()[activity_name]["participants"]

    def test_multiple_students_signup_for_same_activity(self, client):
        """
        Verify that multiple different students can sign up for the same activity.
        
        Arrange: One activity (Drama Club) and two new students
        Act: Both students sign up for Drama Club
        Assert: Both appear in participants list
        """
        # Arrange
        activity_name = "Drama Club"
        student1 = "actor1@mergington.edu"
        student2 = "actor2@mergington.edu"

        # Act - Step 1: First student signs up
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student1}
        )
        assert response1.status_code == 200

        # Act - Step 2: Second student signs up
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student2}
        )
        assert response2.status_code == 200

        # Assert: Both are in the participants list
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        assert student1 in participants
        assert student2 in participants
