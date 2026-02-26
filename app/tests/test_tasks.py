import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from unittest.mock import MagicMock
from app.database import Base
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.routers.tasks import create_task, update_task, delete_task, get_tasks
from app.depsjwt import get_current_user_from_cookies

@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:', connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autoflush=
                                       False, autocommit=False,bind=engine)

    Base.metadata.create_all(engine)
    db=TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(engine)

@pytest.fixture
def mock_user():
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.role="user"
    mock_user.email = "tester@example.com"
    return mock_user

@pytest.fixture
def override_get_current_user(mock_user):
    def _get_mock_user():
        return mock_user
    app.dependency_overrides[get_current_user_from_cookies]=_get_mock_user
    yield
    app.dependency_overrides.clear()

#Testing Create Tasks------------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_task(override_get_current_user, db_session
                           ):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        task_data={
            "title":"Testing tasks with async",
            "description":"Hope it doesn't have any bugs"
        }

        response=await ac.post("/tasks/", json=task_data)

    assert response.status_code == 200
    data=response.json()
    assert data["owner_id"] == 1
    assert data["title"] == "Testing tasks with async"

#Testing Get Tasks------------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_get_tasks_as_user(override_get_current_user):
    mock_user=MagicMock()
    mock_user.id=1
    mock_user.role="user"
    mock_user.email="illaks@gmail.com"

    app.dependency_overrides[get_current_user_from_cookies]=lambda :mock_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response= await ac.get("/tasks/")

        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_tasks_as_admin(override_get_current_user):
    mock_user=MagicMock()
    mock_user.id=2
    mock_user.role="admin"
    mock_user.email=""

    app.dependency_overrides[get_current_user_from_cookies]=lambda :mock_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response= await ac.get("/tasks/")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    app.dependency_overrides.clear()

#Testing Update Tasks------------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_update_task(override_get_current_user,db_session):

    owner_user = MagicMock()
    owner_user.id = 1
    owner_user.role = "user"
    app.dependency_overrides[get_current_user_from_cookies] = lambda: owner_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:

        create_resp = await ac.post("/tasks/", json={"title": "Original", "description": "Owner is 1"})
        task_id = create_resp.json()["id"]


        wrong_user = MagicMock()
        wrong_user.id = 99
        wrong_user.role = "user"
        app.dependency_overrides[get_current_user_from_cookies] = lambda: wrong_user


        response = await ac.put(f"/tasks/{task_id}", json={"title": "Hacked!"})


        assert response.status_code == 403
        assert response.json()["detail"] == "Not Allowed"

#Testing Update Tasks------------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_delete_task_forbidden(override_get_current_user):

    owner = MagicMock()
    owner.id = 1
    owner.role = "user"
    app.dependency_overrides[get_current_user_from_cookies] = lambda: owner

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_resp = await ac.post("/tasks/", json={"title": "Private Task", "description": "Don't touch"})
        task_id = create_resp.json()["id"]


        hacker = MagicMock()
        hacker.id = 99
        hacker.role = "user"
        app.dependency_overrides[get_current_user_from_cookies] = lambda: hacker


        response = await ac.delete(f"/tasks/{task_id}")

        assert response.status_code == 403
        assert response.json()["detail"] == "Not Allowed"