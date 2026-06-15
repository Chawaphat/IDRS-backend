import uuid
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# นำเข้าโมดูลจากโปรเจกต์ของคุณ
from app.main import app 
from app.core.database import get_session
from app.core.authen import verify_token
from app.models.profile import Profile

# 1. Setup In-Memory Database สำหรับการรัน Test (เพื่อไม่ให้กระทบ Database จริง)
engine = create_engine(
    "sqlite://", 
    connect_args={"check_same_thread": False}, 
    poolclass=StaticPool
)

# ให้ SQLite ข้ามการสร้าง ARRAY ที่มันไม่รองรับให้เป็น JSON หรือ TEXT หรือ ข้ามมันไปตอน Test
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler
from sqlalchemy import ARRAY

from sqlalchemy.dialects.postgresql import JSONB

def visit_ARRAY(self, type_, **kw):
    return "JSON"

def visit_JSONB(self, type_, **kw):
    return "JSON"
    
SQLiteTypeCompiler.visit_ARRAY = visit_ARRAY
SQLiteTypeCompiler.visit_JSONB = visit_JSONB

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
        
    # Override Database Session
    app.dependency_overrides[get_session] = get_session_override
    
    client = TestClient(app)
    yield client
    # ล้างค่า overrides หลังเสร็จสิ้นการ Test
    app.dependency_overrides.clear()

# ==========================================
# Test Cases สำหรับ Authentication & Profile
# ==========================================

def test_get_me_success(client: TestClient, session: Session):
    # 1. เตรียมข้อมูล Mock Profile
    user_id = uuid.uuid4()
    mock_profile = Profile(
        id=user_id, 
        email="test@test.com", 
        role="dentist", 
        full_name="Test Name"
    )
    session.add(mock_profile)
    session.commit()

    # 2. Mock Token ที่มาจาก Supabase
    def override_verify_token():
        return {"sub": str(user_id)} # จำลองว่า Payload ของ JWT มีค่า sub เป็น user_id นี้
        
    app.dependency_overrides[verify_token] = override_verify_token

    # 3. ทดสอบเรียก API ดึงข้อมูลส่วนตัว 
    response = client.get("/profiles/me")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(user_id)
    assert data["full_name"] == "Test Name"

def test_update_profile_success(client: TestClient, session: Session):
    # 1. เตรียมข้อมูล
    user_id = uuid.uuid4()
    mock_profile = Profile(
        id=user_id, 
        email="update@test.com", 
        role="dentist", 
        full_name="Old Name"
    )
    session.add(mock_profile)
    session.commit()

    # 2. Mock Token ให้เป็นเจ้าของ Profile
    app.dependency_overrides[verify_token] = lambda: {"sub": str(user_id)}

    # 3. Payload สำหรับอัปเดต
    update_data = {
        "full_name": "New Name Updated"
    }

    # ทดสอบเรียก API Update
    response = client.put(f"/profiles/{user_id}", json=update_data)
    
    assert response.status_code == 200
    assert response.json()["full_name"] == "New Name Updated"

def test_update_profile_unauthorized(client: TestClient, session: Session):
    # 1. เตรียมข้อมูล
    target_user_id = uuid.uuid4()
    other_user_id = uuid.uuid4()
    
    mock_profile = Profile(
        id=target_user_id, 
        email="target@test.com", 
        role="dentist",
        full_name="Target Name"
    )
    other_profile = Profile(
        id=other_user_id, 
        email="other@test.com", 
        role="dentist",
        full_name="Other Name"
    )
    session.add(mock_profile)
    session.add(other_profile)
    session.commit()

    # 2. Mock Token ให้เป็นของ User อีกคน (แต่พยายามไปแก้ไข Profile ของเพื่อน)
    app.dependency_overrides[verify_token] = lambda: {"sub": str(other_user_id)}

    update_data = {"full_name": "Hacked Name"}

    # 3. ผู้ใช้พยายามแก้ไข Profile ID ของคนอื่น
    response = client.put(f"/profiles/{target_user_id}", json=update_data)
    
    # ควรจะถูกระงับด้วย require_profile_owner (403 Forbidden)
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized"