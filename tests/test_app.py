from httpx import AsyncClient, ASGITransport
from main import app
import pytest
from db.db_connection import init_db


@pytest.fixture(scope="session", autouse=True)
def initialize_database():
    import asyncio
    asyncio.run(init_db())


user_token = ""
admin_token = ""


@pytest.mark.asyncio
async def test_register_user():
    transport = ASGITransport(app=app)
    async with AsyncClient(
            transport=transport,
            base_url="http://test"
    ) as client:
        response = await client.post("/register", json={
            "username": "bogdan",
            "password": "bogdan",
            "confirm_password": "bogdan",
            "email": "bogdan@gmail.com"
        })
        assert response.status_code in [200, 400]


@pytest.mark.asyncio
async def test_login_user():
    global user_token
    transport = ASGITransport(app=app)
    async with AsyncClient(
            transport=transport,
            base_url="http://test"
    ) as client:
        response = await client.post("/login", json={
            "username": "bogdan",
            "password": "bogdan"
        })
        assert response.status_code == 200
        user_token = response.json()["access_token"]


@pytest.mark.asyncio
async def test_login_user_invalid():
    transport = ASGITransport(app=app)
    async with AsyncClient(
            transport=transport,
            base_url="http://test"
    ) as client:
        response = await client.post("/login", json={
            "username": "bogdan",
            "password": "1==1"
        })
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_use_token_to_call_ops():
    transport = ASGITransport(app=app)
    async with AsyncClient(
            transport=transport,
            base_url="http://test"
    ) as client:
        response = await client.get("/fibonacci/10", headers={
            "Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200
        assert response.json()["result"] == 55

        response = await client.get("/factorial/5", headers={
            "Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200
        assert response.json()["result"] == 120

        response = await client.get("/pow/2/3", headers={
            "Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200
        assert response.json()["result"] == 8


@pytest.mark.asyncio
async def test_secure_history():
    transport = ASGITransport(app=app)
    async with AsyncClient(
            transport=transport,
            base_url="http://test"
    ) as client:
        response = await client.get("/secure-history", headers={
            "Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200
        assert "history" in response.json()


@pytest.mark.asyncio
async def test_register_admin():
    transport = ASGITransport(app=app)
    async with AsyncClient(
            transport=transport,
            base_url="http://test"
    ) as client:
        await client.post("/register", json={
            "username": "admin",
            "email": "admin@test.com",
            "password": "admin",
            "confirm_password": "admin",
            "role": "admin"
        })


@pytest.mark.asyncio
async def test_admin_login():
    global admin_token
    transport = ASGITransport(app=app)
    async with AsyncClient(
            transport=transport,
            base_url="http://test"
    ) as client:
        response = await client.post("/login", json={
            "username": "admin",
            "password": "admin"
        })
        assert response.status_code == 200
        admin_token = response.json()["access_token"]


@pytest.mark.asyncio
async def test_admin_sees_all():
    transport = ASGITransport(app=app)
    async with AsyncClient(
            transport=transport,
            base_url="http://test"
    ) as client:
        response = await client.get("/secure-history", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        assert len(response.json()["history"]) >= 1


@pytest.mark.asyncio
async def test_delete_user():
    transport = ASGITransport(app=app)
    async with AsyncClient(
            transport=transport,
            base_url="http://test"
    ) as client:
        response = await client.delete("/delete-user/bogdan", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_token_invalid_after_delete():
    transport = ASGITransport(app=app)
    async with AsyncClient(
            transport=transport,
            base_url="http://test"
    ) as client:
        response = await client.get("/secure-history", headers={
            "Authorization": f"Bearer {user_token}"
        })
        assert response.status_code == 401
