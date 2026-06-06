import base64
import os
import pickle
import tempfile

import numpy as np
from flask import current_app


def _get_deepface():
    from deepface import DeepFace
    return DeepFace


def _save_temp_image(base64_str: str) -> str:
    _, encoded = base64_str.split(",", 1)
    data = base64.b64decode(encoded)
    fd, path = tempfile.mkstemp(suffix=".jpg")
    with os.fdopen(fd, "wb") as f:
        f.write(data)
    return path


def _get_user_dir(username: str) -> str:
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], username)
    os.makedirs(path, exist_ok=True)
    return path


def _get_embeddings_path(username: str) -> str:
    return os.path.join(_get_user_dir(username), "embeddings.pkl")


def _get_embedding(image_path: str) -> list:
    DeepFace = _get_deepface()
    result = DeepFace.represent(
        img_path=image_path,
        model_name=current_app.config["FACE_MODEL_NAME"],
        detector_backend=current_app.config["FACE_DETECTOR_BACKEND"],
        enforce_detection=True,
    )
    return result[0]["embedding"]


def enroll_faces(username: str, images: dict) -> None:
    for angle in ("frontal", "left", "right"):
        if angle not in images:
            raise ValueError(f"Missing {angle} face image")

    temp_paths = {}
    try:
        embeddings = {}
        for angle in ("frontal", "left", "right"):
            temp_path = _save_temp_image(images[angle])
            temp_paths[angle] = temp_path
            embedding = _get_embedding(temp_path)
            embeddings[angle] = embedding

        user_dir = _get_user_dir(username)
        with open(os.path.join(user_dir, "embeddings.pkl"), "wb") as f:
            pickle.dump(embeddings, f)
    finally:
        for path in temp_paths.values():
            if os.path.exists(path):
                os.remove(path)


def verify_face(username: str, image_base64: str, threshold: float = None) -> bool:
    temp_path = None
    try:
        threshold = threshold or current_app.config["FACE_MATCH_THRESHOLD"]
        embeddings_path = _get_embeddings_path(username)

        if not os.path.exists(embeddings_path):
            return False

        with open(embeddings_path, "rb") as f:
            enrolled = pickle.load(f)

        temp_path = _save_temp_image(image_base64)
        embedding = _get_embedding(temp_path)

        best = min(
            np.linalg.norm(np.array(embedding) - np.array(ref))
            for ref in enrolled.values()
        )

        return float(best) < threshold
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def is_enrolled(username: str) -> bool:
    return os.path.exists(_get_embeddings_path(username))
