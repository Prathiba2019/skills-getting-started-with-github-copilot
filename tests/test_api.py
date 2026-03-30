from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def setup_module(module):
    # Reset in-memory activities to known state before tests
    activities.clear()
    activities.update({
        "Test Club": {
            "description": "A test activity",
            "schedule": "Now",
            "max_participants": 3,
            "participants": []
        }
    })


def test_signup_success_and_duplicate_prevention():
    # Arrange
    email = "tester@example.com"
    activity = "Test Club"

    # Act - first signup should succeed
    resp1 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp1.status_code == 200
    assert "Signed up" in resp1.json().get("message", "")

    # Act - duplicate signup should be rejected
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 400
    assert resp2.json().get("detail") == "Student is already signed up"

    # Verify stored participant normalized
    assert activities[activity]["participants"][0] == email


def test_unregistered_participant_removal():
    # Arrange
    email = "remove_me@example.com"
    activity = "Test Club"

    # Add participant directly to state
    activities[activity]["participants"].append(email)

    # Act - delete endpoint should remove the participant
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    assert "Removed" in resp.json().get("message", "")

    # Assert participant is gone
    assert all(p != email for p in activities[activity]["participants"]) 


def test_delete_nonexistent_participant():
    # Arrange
    activity = "Test Club"
    email = "doesnotexist@example.com"

    # Ensure email not present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Act
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 404
    assert resp.json().get("detail") == "Participant not found"
