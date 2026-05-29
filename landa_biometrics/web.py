from __future__ import annotations

from functools import wraps

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for

from .auth import BankAuthService
from .config import MAX_CONTENT_LENGTH, SECRET_KEY, STATIC_DIR, TEMPLATE_DIR, FACE_POSES
from .face_service import FaceService
from .storage import Storage


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get("user_id") is None:
            flash("Debes iniciar sesión primero.", "warning")
            return redirect(url_for("index"))
        return view(*args, **kwargs)

    return wrapped_view


class AppContext:
    def __init__(self) -> None:
        self.storage = Storage()
        self.face_service = FaceService(self.storage)
        self.auth = BankAuthService(self.storage, self.face_service)


def create_app() -> Flask:
    app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=str(STATIC_DIR))
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
    context = AppContext()

    @app.get("/")
    def index():
        if session.get("user_id") is not None:
            return redirect(url_for("dashboard"))
        return render_template("auth.html")

    @app.post("/signup")
    def signup():
        username = request.form.get("username", "")
        full_name = request.form.get("full_name", "")
        password = request.form.get("password", "")
        try:
            context.auth.signup(username=username, full_name=full_name, password=password)
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("index"))

        flash("Cuenta creada. Ahora inicia sesión con tus credenciales.", "success")
        return redirect(url_for("index"))

    @app.post("/login/password")
    def login_password():
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        try:
            user = context.auth.login_with_password(username=username, password=password)
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("index"))

        session["user_id"] = user.id
        flash(f"Bienvenido, {user.full_name}.", "success")
        return redirect(url_for("dashboard"))

    @app.post("/login/face/start")
    def start_face_login():
        username = request.form.get("username", "").strip().lower()
        if not username:
            flash("Debes escribir tu usuario para iniciar el reconocimiento facial.", "error")
            return redirect(url_for("index"))

        user = context.storage.get_user_by_username(username)
        if user is None:
            flash("El usuario no existe.", "error")
            return redirect(url_for("index"))
        if not user.face_enabled:
            flash("Ese usuario todavía no tiene el reconocimiento facial activo.", "warning")
            return redirect(url_for("index"))

        session["face_login_username"] = user.username
        session["face_flow"] = "login"
        session["face_pose_index"] = 0
        return render_template("face_wizard.html", mode="login", username=user.username, full_name=user.full_name, poses=FACE_POSES)

    @app.get("/settings")
    @login_required
    def settings():
        user = context.storage.get_user_by_id(session["user_id"])
        if user is None:
            session.clear()
            flash("La sesión no es válida.", "error")
            return redirect(url_for("index"))
        sample_count = context.storage.face_sample_count(user.id)
        return render_template("dashboard.html", user=user, sample_count=sample_count, events=context.storage.recent_events())

    @app.post("/settings/password")
    @login_required
    def change_password():
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        try:
            context.auth.change_password(session["user_id"], current_password=current_password, new_password=new_password)
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("settings"))

        flash("Tu contraseña fue actualizada.", "success")
        return redirect(url_for("settings"))

    @app.post("/settings/face/toggle")
    @login_required
    def toggle_face():
        enabled = request.form.get("enabled") == "1"
        try:
            if enabled and context.storage.face_sample_count(session["user_id"]) < len(FACE_POSES):
                flash("Primero debes completar el registro facial con las tres capturas.", "warning")
                return redirect(url_for("face_enroll"))
            context.auth.enable_face_login(session["user_id"], enabled)
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("settings"))

        flash("Preferencia facial actualizada.", "success")
        return redirect(url_for("settings"))

    @app.get("/face/enroll")
    @login_required
    def face_enroll():
        user = context.storage.get_user_by_id(session["user_id"])
        if user is None:
            session.clear()
            flash("La sesión no es válida.", "error")
            return redirect(url_for("index"))
        session["face_flow"] = "enroll"
        session["face_pose_index"] = 0
        return render_template("face_wizard.html", mode="enroll", username=user.username, full_name=user.full_name, poses=FACE_POSES)

    @app.post("/api/face/capture")
    def api_face_capture():
        mode = request.form.get("mode", "")
        pose = request.form.get("pose", "")
        step_index = int(request.form.get("step_index", "0"))
        final_step = request.form.get("final_step", "false") == "true"
        frame = request.files.get("frame")
        if frame is None or frame.filename == "":
            return jsonify({"ok": False, "message": "No se recibió ninguna captura."}), 400

        image_bytes = frame.read()

        if mode == "enroll":
            user_id = session.get("user_id")
            if user_id is None:
                return jsonify({"ok": False, "message": "Debes iniciar sesión primero."}), 401
            try:
                context.auth.enroll_face_step(user_id=user_id, pose_label=pose, image_bytes=image_bytes)
                if final_step:
                    context.auth.finalize_face_enrollment(user_id)
            except ValueError as exc:
                return jsonify({"ok": False, "message": str(exc)}), 400

            next_step = step_index + 1
            return jsonify({
                "ok": True,
                "message": "Captura guardada correctamente.",
                "next_step": next_step,
                "complete": final_step,
                "redirect_url": url_for("settings") if final_step else None,
            })

        if mode == "login":
            username = session.get("face_login_username")
            if username is None:
                return jsonify({"ok": False, "message": "La sesión facial no está activa."}), 401
            try:
                result = context.auth.verify_face_login(username=username, image_bytes=image_bytes)
            except ValueError as exc:
                return jsonify({"ok": False, "message": str(exc)}), 400

            if not result.matched:
                return jsonify({"ok": False, "message": result.note}), 401

            if final_step:
                user = context.storage.get_user_by_username(username)
                if user is None:
                    return jsonify({"ok": False, "message": "No fue posible confirmar el usuario."}), 400
                session.pop("face_login_username", None)
                session.pop("face_flow", None)
                session.pop("face_pose_index", None)
                session["user_id"] = user.id
                return jsonify({"ok": True, "message": "Acceso facial aprobado.", "complete": True, "redirect_url": url_for("settings")})

            return jsonify({"ok": True, "message": "Rostro validado.", "next_step": step_index + 1, "complete": False})

        return jsonify({"ok": False, "message": "Modo no soportado."}), 400

    @app.post("/logout")
    @login_required
    def logout():
        session.clear()
        flash("Sesión cerrada.", "success")
        return redirect(url_for("index"))

    @app.get("/dashboard")
    @login_required
    def dashboard():
        user = context.storage.get_user_by_id(session["user_id"])
        if user is None:
            session.clear()
            flash("La sesión expiró.", "error")
            return redirect(url_for("index"))
        sample_count = context.storage.face_sample_count(user.id)
        events = context.storage.recent_events()
        return render_template("dashboard.html", user=user, sample_count=sample_count, events=events)

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "landa-biometrics"}

    return app
