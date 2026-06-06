import base64

import pytest

from app.face_service import is_enrolled

# Minimal valid 1x1 JPEG in base64
_VALID_JPEG_B64 = (
    "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP////////////////////////////////////////////////////////////////////"
    "//////////////////////////////////////////////////////2wBDAf/////////////////////////////////////////////////////////////////"
    "///////////////////////////////////////////////////////wAARCAABAAEDASIA"
    "AhEBAxEB/8QAFAABAAAAAAAAAAAAAAAAAAAACf/EABQQAQAAAAAAAAAAAAAAAAAAAAD/"
    "xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMR"
    "AD8AANL/2Q=="
)


def test_is_enrolled_no_user(app):
    with app.app_context():
        assert is_enrolled("nonexistent_user") is False


def test_is_enrolled_empty_username(app):
    with app.app_context():
        assert is_enrolled("") is False


def test_enroll_faces_missing_data(app):
    from app.face_service import enroll_faces
    with app.app_context():
        try:
            enroll_faces("testuser", {})
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Missing" in str(e)


def test_enroll_faces_missing_angle(app):
    from app.face_service import enroll_faces
    data_uri = "data:image/jpeg;base64," + _VALID_JPEG_B64
    with app.app_context():
        try:
            enroll_faces("testuser", {"frontal": data_uri})
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Missing left face" in str(e)


def test_verify_face_no_enrollment(app):
    from app.face_service import verify_face
    with app.app_context():
        result = verify_face("nonexistent", "data:image/jpeg;base64," + _VALID_JPEG_B64)
        assert result is False
