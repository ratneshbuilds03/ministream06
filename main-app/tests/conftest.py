import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import AsyncMock,MagicMock,patch
from app.main import app
from app.database import Base,get_db
from app.models.user import User,UserRole
from app.models.content import Content,ContentStatus
from app.models.subscription import Subscription
from passlib.context import CryptContext


TEST_DB_URL ="sqlite:///./test_ministream.db"
test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread":False}
)
TestSession = sessionmaker(autocommit=False,autoflush=False,bind=test_engine)
pwd = CryptContext(schemes=["bcrypt"],deprecated="auto")

def override_get_db():
    db=TestSession()
    try:
        yield db
    finally:
        db.close()
        
class MockCollection:
    def __init__(self):
        self._data = []

    async def insert_one(self, doc):
        self._data.append(doc)
        return MagicMock(inserted_id="mock_id_123")

    async def find_one(self, query):
        return None

    def find(self, query=None, projection=None):
        return MockCursor([])

    async def count_documents(self, query):
        return 0

    def sort(self, *args):
        return self

    async def create_index(self, *args):
        pass

    async def update_one(self, *args, **kwargs):
        return MagicMock(modified_count=1)

class MockCursor:
    def __init__(self, data):
        self._data = data

    def sort(self, *args):
        return self

    def skip(self, n):
        return self

    def limit(self, n):
        return self

    async def to_list(self, length=None):
        return self._data

class MockMongoDB:
    def __init__(self):
        self.comments = MockCollection()

mock_mongo = MockMongoDB()

def override_get_mongodb():
    return mock_mongo

@pytest.fixture(scope="session")
def client():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db

    from app.mongodb import get_mongodb
    app.dependency_overrides[get_mongodb] = override_get_mongodb

    with TestClient(app) as c:
        yield c

    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def db():
    db = TestSession()
    try:
        yield db
    finally:
        db.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
        db.close()

@pytest.fixture
def creator_user(db):
    user = User(
        name="Test Creator",
        username="testcreator",
        email="creator@test.com",
        password_hash=pwd.hash("test123"),
        role=UserRole.CREATOR,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def viewer_user(db):
    user = User(
        name="Test Viewer",
        username="testviewer",
        email="viewer@test.com",
        password_hash=pwd.hash("test123"),
        role=UserRole.VIEWER,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def creator_token(client, creator_user):
    response = client.post("/auth/login", data={
        "username": "creator@test.com",
        "password": "test123"
    })
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def viewer_token(client, viewer_user):
    response = client.post("/auth/login", data={
        "username": "viewer@test.com",
        "password": "test123"
    })
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def creator_headers(creator_token):
    return {"Authorization": f"Bearer {creator_token}"}

@pytest.fixture
def viewer_headers(viewer_token):
    return {"Authorization": f"Bearer {viewer_token}"}

@pytest.fixture
def published_content(db, creator_user):
    content = Content(
        title="Test Python Tutorial",
        description="Learn Python basics",
        content_type="video",
        status=ContentStatus.PUBLISHED,
        category="Technology",
        tags="python,tutorial",
        views_count=100,
        likes_count=10,
        creator_id=creator_user.id
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    return content