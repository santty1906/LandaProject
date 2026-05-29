from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from .config import FACE_IMAGE_SIZE, FACE_POSES, MAX_BRIGHTNESS, MATCH_THRESHOLD, MIN_BRIGHTNESS, MIN_FACE_AREA, MIN_SHARPNESS
from .storage import Storage


@dataclass(slots=True)
class ImageQuality:
    brightness: float
    sharpness: float
    face_area: int
    accepted: bool
    notes: list[str]


@dataclass(slots=True)
class RecognitionResult:
    matched: bool
    score: float
    matched_user_id: int | None
    note: str


class FaceService:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage
        self.has_lbph = hasattr(cv2, "face") and hasattr(cv2.face, "LBPHFaceRecognizer_create")

    def process_capture(self, image_bytes: bytes) -> tuple[np.ndarray, ImageQuality]:
        buffer = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("No se pudo leer la captura")

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        face = self._center_crop(gray)
        if face.size == 0:
            raise ValueError("La captura no contiene un rostro válido")

        quality = self._assess_quality(face)
        normalized = cv2.resize(face, (FACE_IMAGE_SIZE, FACE_IMAGE_SIZE), interpolation=cv2.INTER_AREA)
        return normalized, quality

    def _center_crop(self, gray: np.ndarray) -> np.ndarray:
        height, width = gray.shape[:2]
        if height < 80 or width < 80:
            return gray

        crop_height = int(height * 0.72)
        crop_width = int(width * 0.72)
        start_y = max(0, (height - crop_height) // 2)
        start_x = max(0, (width - crop_width) // 2)
        end_y = min(height, start_y + crop_height)
        end_x = min(width, start_x + crop_width)
        return gray[start_y:end_y, start_x:end_x]

    def _assess_quality(self, face_gray: np.ndarray) -> ImageQuality:
        brightness = float(np.mean(face_gray))
        sharpness = float(cv2.Laplacian(face_gray, cv2.CV_64F).var())
        area = int(face_gray.shape[0] * face_gray.shape[1])
        notes: list[str] = []
        accepted = True

        if area < MIN_FACE_AREA:
            accepted = False
            notes.append("La cara debe ocupar una porción mayor de la pantalla.")
        if sharpness < MIN_SHARPNESS:
            accepted = False
            notes.append("La imagen está borrosa.")
        if brightness < MIN_BRIGHTNESS:
            accepted = False
            notes.append("La imagen está demasiado oscura.")
        if brightness > MAX_BRIGHTNESS:
            accepted = False
            notes.append("La imagen está demasiado iluminada.")

        return ImageQuality(brightness=brightness, sharpness=sharpness, face_area=area, accepted=accepted, notes=notes)

    @staticmethod
    def image_to_blob(face_gray: np.ndarray) -> bytes:
        return face_gray.astype(np.uint8).tobytes()

    @staticmethod
    def blob_to_image(image_blob: bytes) -> np.ndarray:
        return np.frombuffer(image_blob, dtype=np.uint8).reshape((FACE_IMAGE_SIZE, FACE_IMAGE_SIZE))

    def store_capture(self, user_id: int, pose_label: str, image_bytes: bytes) -> ImageQuality:
        if pose_label not in FACE_POSES:
            raise ValueError("La pose solicitada no es válida")

        face_image, quality = self.process_capture(image_bytes)
        if not quality.accepted:
            raise ValueError("La captura no cumple la calidad mínima")

        self.storage.save_face_sample(user_id=user_id, pose_label=pose_label, image_blob=self.image_to_blob(face_image))
        return quality

    def recognize(self, image_bytes: bytes, expected_user_id: int) -> RecognitionResult:
        face_image, quality = self.process_capture(image_bytes)
        if not quality.accepted:
            return RecognitionResult(matched=False, score=0.0, matched_user_id=None, note="La captura no cumple la calidad mínima")

        samples = self.storage.list_face_samples()
        if not samples:
            return RecognitionResult(matched=False, score=0.0, matched_user_id=None, note="No hay muestras faciales registradas")

        if self.has_lbph:
            recognizer = cv2.face.LBPHFaceRecognizer_create(radius=1, neighbors=8, grid_x=8, grid_y=8)
            images = [self.blob_to_image(row["image_blob"]) for row in samples]
            labels = np.array([row["user_id"] for row in samples], dtype=np.int32)
            recognizer.train(images, labels)
            label, confidence = recognizer.predict(face_image)
            score = max(0.0, 100.0 - float(confidence))
            if label == expected_user_id and confidence <= MATCH_THRESHOLD:
                return RecognitionResult(matched=True, score=score, matched_user_id=label, note="Coincidencia facial aprobada")
            return RecognitionResult(matched=False, score=score, matched_user_id=label, note="La coincidencia facial no alcanzó el umbral")

        score = self._cosine_fallback(face_image, expected_user_id, samples)
        return RecognitionResult(matched=score >= 75.0, score=score, matched_user_id=expected_user_id if score >= 75.0 else None, note="Comparación por similitud básica")

    def _cosine_fallback(self, face_image: np.ndarray, expected_user_id: int, samples: list[object]) -> float:
        live_vector = face_image.astype(np.float32).flatten()
        live_norm = float(np.linalg.norm(live_vector))
        if live_norm == 0.0:
            return 0.0
        live_vector = live_vector / live_norm

        candidate_vectors: list[np.ndarray] = []
        for row in samples:
            if row["user_id"] != expected_user_id:
                continue
            stored = self.blob_to_image(row["image_blob"]).astype(np.float32).flatten()
            stored_norm = float(np.linalg.norm(stored))
            if stored_norm == 0.0:
                continue
            candidate_vectors.append(stored / stored_norm)

        if not candidate_vectors:
            return 0.0

        similarities = [float(np.dot(live_vector, vector)) for vector in candidate_vectors]
        return max(similarities) * 100.0
