import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

from landa_biometrics.auth import BankAuthService
from landa_biometrics.face_service import FaceService
from landa_biometrics.storage import Storage


def make_test_capture() -> bytes:
    image = np.full((480, 640, 3), 105, dtype=np.uint8)
    cv2.circle(image, (320, 220), 90, (160, 160, 160), -1)
    cv2.circle(image, (290, 205), 18, (28, 28, 28), -1)
    cv2.circle(image, (350, 205), 18, (28, 28, 28), -1)
    cv2.ellipse(image, (320, 255), (36, 18), 0, 0, 180, (45, 45, 45), 4)
    cv2.line(image, (250, 180), (390, 180), (70, 70, 70), 3)
    cv2.line(image, (245, 235), (395, 235), (95, 95, 95), 2)
    cv2.line(image, (260, 300), (380, 300), (180, 180, 180), 2)
    cv2.line(image, (0, 0), (639, 479), (70, 70, 70), 1)
    cv2.line(image, (639, 0), (0, 479), (70, 70, 70), 1)
    cv2.putText(image, "LANDA", (210, 390), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (210, 210, 210), 3)
    ok, encoded = cv2.imencode(".jpg", image)
    if not ok:
        raise RuntimeError("No se pudo crear la captura de prueba")
    return encoded.tobytes()


class StorageTests(unittest.TestCase):
    def test_signup_password_and_events(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = Storage(Path(temp_dir) / "landa-test.db")
            face_service = FaceService(storage)
            auth = BankAuthService(storage, face_service)

            user = auth.signup("maria.g", "Maria Gonzalez", "secret123")
            self.assertEqual(user.username, "maria.g")

            logged_user = auth.login_with_password("maria.g", "secret123")
            self.assertEqual(logged_user.id, user.id)

            events = storage.recent_events()
            self.assertGreaterEqual(len(events), 2)

    def test_face_enrollment_three_poses(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = Storage(Path(temp_dir) / "landa-test.db")
            face_service = FaceService(storage)
            auth = BankAuthService(storage, face_service)

            user = auth.signup("juan.p", "Juan Perez", "secret123")
            for pose in ("frontal", "izquierda", "derecha"):
                auth.enroll_face_step(user.id, pose, make_test_capture())

            auth.finalize_face_enrollment(user.id)
            stored_user = storage.get_user_by_id(user.id)

            self.assertIsNotNone(stored_user)
            self.assertTrue(stored_user.face_enabled)
            self.assertEqual(storage.face_sample_count(user.id), 3)


if __name__ == "__main__":
    unittest.main()
