import time
import uuid
import pytest


pytestmark = [pytest.mark.anyio]


async def test_create_parcel(api_client):
    response = await api_client.get("/docs")
    assert response.status_code == 200

    parcel = {"name": "jacket", "weight": 0.5, "type_id": 1, "value_in_dollars": 50}
    response = await api_client.post("/parcel", json=parcel)
    assert response.status_code == 200
    assert response.json()["data"]["parcel_id"] != None

    parcel["weight"] = 0
    response = await api_client.post("/parcel", json=parcel)
    assert response.status_code == 422

    parcel["weight"], parcel["type_id"] = 0.5, 5
    response = await api_client.post("/parcel", json=parcel)
    assert response.status_code == 422


async def test_get_parcel_type(api_client):
    response = await api_client.get("/docs")
    assert response.status_code == 200

    response = await api_client.get("/parcel_type")
    assert response.status_code == 200
    assert response.json()["data"]["1"] == "одежда"
    assert response.json()["message"] == "Все типы посылок"


async def test_get_parcel_by_client(api_client):
    response = await api_client.get(
        "/parcel", cookies={"session_id": str(uuid.uuid4())}
    )
    assert response.status_code == 200
    assert response.json()["detail"]["status"] == "error"
    for i in range(3):
        parcel = {"name": "jacket", "weight": 0.5, "type_id": 1, "value_in_dollars": 50}
        response = await api_client.post("/parcel", json=parcel)
        assert response.status_code == 200

    time.sleep(5)
    response = await api_client.get("/parcel", params={"type_id": 1})
    assert response.status_code == 200
    assert response.json()["data"][0]["weight"] == 0.5
    assert len(response.json()["data"]) == 3

    response = await api_client.get("/parcel", params={"price_calculated": True})
    assert response.status_code == 200
    assert isinstance(response.json()["data"][0]["price"], float)
    assert len(response.json()["data"]) == 3

    response = await api_client.get("/parcel", params={"limit": 2})
    assert response.status_code == 200
    assert isinstance(response.json()["data"][0]["price"], float)
    assert len(response.json()["data"]) == 2


async def test_get_parcel(api_client):
    parcel = {"name": "jacket", "weight": 0.5, "type_id": 1, "value_in_dollars": 50}
    session_id = str(uuid.uuid4())
    response = await api_client.post(
        "/parcel", json=parcel, cookies={"session_id": session_id}
    )
    assert response.status_code == 200

    parcel_id = response.json()["data"]["parcel_id"]
    response = await api_client.get(
        f"/parcel/{parcel_id}", cookies={"session_id": str(uuid.uuid4())}
    )
    assert response.status_code == 403
    assert response.json()["detail"]["message"] == "Нет доступа к данным этой посылки."

    response = await api_client.get(
        f"/parcel/{parcel_id}", cookies={"session_id": session_id}
    )
    assert response.status_code == 200
    assert response.json()["data"]["price"] == "Не рассчитано"

    response = await api_client.get(
        "/parcel/3987002", cookies={"session_id": session_id}
    )
    assert response.status_code == 404
    assert response.json()["detail"]["status"] == "error"

    time.sleep(60)

    response = await api_client.get(
        f"/parcel/{parcel_id}", cookies={"session_id": session_id}
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"]["price"], float)


async def test_get_rate(api_client):
    response = await api_client.get(
        "/admin/calculate_rate", params={"admin_session": "123"}
    )
    assert response.status_code == 200

    response = await api_client.get(
        "/admin/calculate_rate", params={"admin_session": "1"}
    )
    assert response.status_code == 403
