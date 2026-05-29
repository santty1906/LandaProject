from __future__ import annotations

from dataclasses import dataclass

from werkzeug.security import check_password_hash, generate_password_hash

from .config import FACE_POSES, MIN_PASSWORD_LENGTH
from .face_service import FaceService, RecognitionResult
from .storage import Storage, UserRecord


@dataclass(slots=True)
class LoginResult:
    user: UserRecord
    note: str


class BankAuthService:
    def __init__(self, storage: Storage, face_service: FaceService) -> None:
        self.storage = storage
        self.face_service = face_service

    def signup(self, username: str, full_name: str, password: str) -> UserRecord:
        username = username.strip().lower()
        full_name = full_name.strip()
        if len(username) < 3:
            raise ValueError("El usuario debe tener al menos 3 caracteres")
        if len(full_name) < 3:
            raise ValueError("El nombre completo es obligatorio")
        if len(password) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres")

        password_hash = generate_password_hash(password)
        user = self.storage.create_user(username=username, full_name=full_name, password_hash=password_hash)
        self.storage.record_event(user_id=user.id, event_type="signup", status="created", note="Cuenta creada correctamente")
        return user

    def login_with_password(self, username: str, password: str) -> UserRecord:
        user = self.storage.get_user_by_username(username.strip().lower())
        if user is None or not check_password_hash(user.password_hash, password):
            self.storage.record_event(user_id=None, event_type="password_login", status="denied", note=f"Intento fallido para {username}")
            raise ValueError("Usuario o contraseña incorrectos")

        self.storage.mark_login(user.id)
        self.storage.record_event(user_id=user.id, event_type="password_login", status="approved", note="Acceso por contraseña")
        return user

    def change_password(self, user_id: int, current_password: str, new_password: str) -> None:
        user = self.storage.get_user_by_id(user_id)
        if user is None:
            raise ValueError("El usuario no existe")
        if not check_password_hash(user.password_hash, current_password):
            raise ValueError("La contraseña actual no es correcta")
        if len(new_password) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"La nueva contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres")

        self.storage.update_password(user_id, generate_password_hash(new_password))
        self.storage.record_event(user_id=user_id, event_type="password_change", status="updated", note="Contraseña actualizada")

    def enable_face_login(self, user_id: int, enabled: bool) -> None:
        self.storage.set_face_enabled(user_id, enabled)
        status = "enabled" if enabled else "disabled"
        self.storage.record_event(user_id=user_id, event_type="face_setting", status=status, note="Preferencia de reconocimiento facial actualizada")

    def enroll_face_step(self, user_id: int, pose_label: str, image_bytes: bytes) -> None:
        if pose_label not in FACE_POSES:
            raise ValueError("La pose indicada no es válida")
        quality = self.face_service.store_capture(user_id=user_id, pose_label=pose_label, image_bytes=image_bytes)
        self.storage.record_event(
            user_id=user_id,
            event_type="face_enroll",
            status="captured",
            similarity=None,
            note=f"Captura {pose_label} aceptada con nitidez {quality.sharpness:.1f}",
        )

    def finalize_face_enrollment(self, user_id: int) -> None:
        sample_count = self.storage.face_sample_count(user_id)
        if sample_count < len(FACE_POSES):
            raise ValueError("Faltan capturas para completar el registro facial")
        self.storage.set_face_enabled(user_id, True)
        self.storage.record_event(user_id=user_id, event_type="face_enroll", status="completed", note="Reconocimiento facial activado")

    def verify_face_login(self, username: str, image_bytes: bytes) -> RecognitionResult:
        user = self.storage.get_user_by_username(username.strip().lower())
        if user is None:
            self.storage.record_event(user_id=None, event_type="face_login", status="denied", note=f"Usuario desconocido: {username}")
            raise ValueError("El usuario no existe")
        if not user.face_enabled:
            self.storage.record_event(user_id=user.id, event_type="face_login", status="denied", note="El reconocimiento facial no está habilitado")
            raise ValueError("El reconocimiento facial no está habilitado para esta cuenta")

        result = self.face_service.recognize(image_bytes=image_bytes, expected_user_id=user.id)
        status = "approved" if result.matched else "denied"
        self.storage.record_event(
            user_id=user.id,
            event_type="face_login",
            status=status,
            similarity=result.score,
            note=result.note,
        )
        if result.matched:
            self.storage.mark_login(user.id)
        return result
