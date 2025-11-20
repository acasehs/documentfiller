"""
Test Suite for DocumentFiller v2.0
Tests authentication, database, and core functionality
"""

import pytest
import asyncio
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.auth import (
    get_password_hash, verify_password, create_access_token, decode_token
)
from backend.database import init_db, SessionLocal, UserModel, DocumentModel
from backend.batch_processor import BatchProcessor, BatchStatus

# ==================== Authentication Tests ====================

def test_password_hashing():
    """Test password hashing and verification"""
    password = "test_password_123"
    hashed = get_password_hash(password)

    # Should not be plain text
    assert hashed != password

    # Should verify correctly
    assert verify_password(password, hashed)

    # Should not verify wrong password
    assert not verify_password("wrong_password", hashed)

    print("✅ Password hashing test passed")

def test_jwt_token_creation():
    """Test JWT token creation and decoding"""
    data = {"sub": "testuser"}
    token = create_access_token(data)

    # Should return a string
    assert isinstance(token, str)
    assert len(token) > 0

    # Should decode correctly
    token_data = decode_token(token)
    assert token_data.username == "testuser"

    print("✅ JWT token creation test passed")

def test_jwt_token_expiration():
    """Test JWT token expiration"""
    data = {"sub": "testuser"}
    # Create token that expires in 1 second
    token = create_access_token(data, expires_delta=timedelta(seconds=1))

    # Should decode immediately
    token_data = decode_token(token)
    assert token_data.username == "testuser"

    print("✅ JWT token expiration test passed")

# ==================== Database Tests ====================

def test_database_initialization():
    """Test database initialization"""
    try:
        init_db()
        print("✅ Database initialization test passed")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

def test_user_creation():
    """Test user creation in database"""
    db = SessionLocal()
    try:
        # Create test user
        test_user = UserModel(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("testpass"),
            is_active=True
        )

        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        # Verify user was created
        assert test_user.id is not None
        assert test_user.email == "test@example.com"
        assert test_user.username == "testuser"
        assert test_user.is_active == True

        # Clean up
        db.delete(test_user)
        db.commit()

        print("✅ User creation test passed")
    except Exception as e:
        db.rollback()
        print(f"❌ User creation failed: {e}")
        raise
    finally:
        db.close()

def test_document_creation():
    """Test document creation with user relationship"""
    db = SessionLocal()
    try:
        # Create test user
        test_user = UserModel(
            email="test2@example.com",
            username="testuser2",
            hashed_password=get_password_hash("testpass"),
            is_active=True
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        # Create document
        test_doc = DocumentModel(
            document_id="test-doc-123",
            filename="test.docx",
            file_path="/tmp/test.docx",
            user_id=test_user.id
        )
        db.add(test_doc)
        db.commit()
        db.refresh(test_doc)

        # Verify document was created
        assert test_doc.id is not None
        assert test_doc.user_id == test_user.id
        assert test_doc.filename == "test.docx"

        # Verify relationship
        assert test_doc.owner.username == "testuser2"

        # Clean up
        db.delete(test_doc)
        db.delete(test_user)
        db.commit()

        print("✅ Document creation test passed")
    except Exception as e:
        db.rollback()
        print(f"❌ Document creation failed: {e}")
        raise
    finally:
        db.close()

# ==================== Batch Processing Tests ====================

@pytest.mark.asyncio
async def test_batch_processor_creation():
    """Test batch processor task creation"""
    processor = BatchProcessor()

    task_id = await processor.create_task(
        document_id="doc-123",
        sections=[
            {"id": "sec-1", "title": "Section 1", "content": ""},
            {"id": "sec-2", "title": "Section 2", "content": ""}
        ],
        operation_mode="REPLACE",
        model="test-model",
        temperature=0.7,
        max_tokens=1000
    )

    # Verify task was created
    assert task_id is not None
    assert task_id in processor.tasks

    task = processor.tasks[task_id]
    assert task.status == BatchStatus.PENDING
    assert task.total_sections == 2
    assert task.completed_sections == 0

    print("✅ Batch processor creation test passed")

@pytest.mark.asyncio
async def test_batch_processor_status():
    """Test batch processor status retrieval"""
    processor = BatchProcessor()

    task_id = await processor.create_task(
        document_id="doc-456",
        sections=[{"id": "sec-1", "title": "Section 1", "content": ""}],
        operation_mode="REPLACE",
        model="test-model",
        temperature=0.7,
        max_tokens=1000
    )

    status = await processor.get_task_status(task_id)

    assert status["task_id"] == task_id
    assert status["status"] == "pending"
    assert status["total_sections"] == 1
    assert status["progress_percentage"] == 0

    print("✅ Batch processor status test passed")

@pytest.mark.asyncio
async def test_batch_processor_empty_filter():
    """Test batch processor empty section filtering"""
    processor = BatchProcessor()

    task_id = await processor.create_task(
        document_id="doc-789",
        sections=[
            {"id": "sec-1", "title": "Section 1", "content": "Has content"},
            {"id": "sec-2", "title": "Section 2", "content": ""},
            {"id": "sec-3", "title": "Section 3", "content": "   "},
        ],
        operation_mode="REPLACE",
        model="test-model",
        temperature=0.7,
        max_tokens=1000,
        process_empty_only=True
    )

    task = processor.tasks[task_id]
    # Should only have sections 2 and 3 (empty/whitespace)
    assert task.total_sections == 2

    print("✅ Batch processor empty filter test passed")

# ==================== Integration Tests ====================

def test_user_authentication_flow():
    """Test complete user authentication flow"""
    db = SessionLocal()
    try:
        # 1. Register user
        username = "integration_test_user"
        password = "test_password_123"
        email = "integration@test.com"

        user = UserModel(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # 2. Verify password
        assert verify_password(password, user.hashed_password)

        # 3. Create token
        token = create_access_token(data={"sub": username})

        # 4. Decode token
        token_data = decode_token(token)
        assert token_data.username == username

        # Clean up
        db.delete(user)
        db.commit()

        print("✅ User authentication flow test passed")
    except Exception as e:
        db.rollback()
        print(f"❌ Authentication flow failed: {e}")
        raise
    finally:
        db.close()

# ==================== Run All Tests ====================

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("DocumentFiller v2.0 Test Suite")
    print("="*60 + "\n")

    # Synchronous tests
    tests = [
        ("Password Hashing", test_password_hashing),
        ("JWT Token Creation", test_jwt_token_creation),
        ("JWT Token Expiration", test_jwt_token_expiration),
        ("Database Initialization", test_database_initialization),
        ("User Creation", test_user_creation),
        ("Document Creation", test_document_creation),
        ("User Authentication Flow", test_user_authentication_flow),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            print(f"\nRunning: {name}")
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            failed += 1

    # Async tests
    async_tests = [
        ("Batch Processor Creation", test_batch_processor_creation),
        ("Batch Processor Status", test_batch_processor_status),
        ("Batch Processor Empty Filter", test_batch_processor_empty_filter),
    ]

    for name, test_func in async_tests:
        try:
            print(f"\nRunning: {name}")
            asyncio.run(test_func())
            passed += 1
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            failed += 1

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Total: {passed + failed}")
    print("="*60 + "\n")

    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
