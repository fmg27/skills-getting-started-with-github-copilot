from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def encode_name(name: str) -> str:
    return quote(name, safe="")


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code in (307, 308)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"
    encoded_activity = encode_name(activity_name)

    response = client.post(f"/activities/{encoded_activity}/signup?email={quote(email, safe='')}" )

    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"


def test_unregister_from_activity_removes_participant():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    encoded_activity = encode_name(activity_name)

    assert email in activities[activity_name]["participants"]

    response = client.delete(f"/activities/{encoded_activity}/unregister?email={quote(email, safe='')}" )

    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"


def test_unregister_nonexistent_participant_returns_error():
    activity_name = "Chess Club"
    email = "missing@mergington.edu"
    encoded_activity = encode_name(activity_name)

    response = client.delete(f"/activities/{encoded_activity}/unregister?email={quote(email, safe='')}" )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"
