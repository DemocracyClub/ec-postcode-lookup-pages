from app import app
from starlette.testclient import TestClient


def test_council_html():
    client = TestClient(app)
    response = client.get("/mock/electoral-services?postcode-search=AA1%201AA")

    assert response.status_code == 200
    assert "Your local council" in response.text
    assert "Stroud Council" in response.text


def test_council_json():
    client = TestClient(app)
    response = client.get(
        "/mock/electoral-services?postcode-search=AA1%201AA&format=json"
    )
    data = response.json()

    assert response.status_code == 200
    assert not data["address_picker"]
    assert data["addresses"] == []
    assert data["electoral_services"]["council_id"] == "STO"


def test_vjb_html():
    client = TestClient(app)
    response = client.get("/mock/electoral-services?postcode-search=AA1%201AP")

    assert response.status_code == 200
    # vjb
    assert "Get help with electoral registration" in response.text
    assert "Lothian Valuation Joint Board" in response.text
    # council
    assert "Your local council" in response.text
    assert "City of Edinburgh Council" in response.text


def test_vjb_json():
    client = TestClient(app)
    response = client.get(
        "/mock/electoral-services?postcode-search=AA1%201AP&format=json"
    )
    data = response.json()

    assert response.status_code == 200
    assert not data["address_picker"]
    assert data["addresses"] == []
    # vjb
    assert data["registration"]["email"] == "enquiries@lothian-vjb.gov.uk"
    # council
    assert data["electoral_services"]["email"] == "elections@edinburgh.gov.uk"
