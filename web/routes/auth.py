"""Auth routes: /, /login, /logout, /app"""
from pathlib import Path
from flask import Blueprint, request, session, redirect, render_template, send_file
from web.auth import verify_login
from logger import get_logger

bp = Blueprint("auth", __name__)
log = get_logger("web.auth.routes")

@bp.route("/")
def index():
    if session.get("logged_in"):
        return redirect("/app")
    return redirect("/login")

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session.get("logged_in"):
            return redirect("/app")
        return render_template("login.html", error=None)

    uid = request.form.get("user_id", "").strip()
    pwd = request.form.get("password", "").strip()
    remember = request.form.get("remember") == "on"

    result = verify_login(uid, pwd)
    if not result.get("ok"):
        return render_template("login.html", error=result.get("error", "خطأ"))

    session.permanent = bool(remember)
    session["logged_in"] = True
    session["user_id"] = result["user_id"]
    session["is_owner"] = bool(result["is_owner"])
    log.info(f"Session established for {result['user_id']}")
    return redirect("/app")

@bp.route("/logout")
def logout():
    uid = session.get("user_id", "?")
    session.clear()
    log.info(f"Logout: {uid}")
    return redirect("/login")

@bp.route("/app")
def app_view():
    if not session.get("logged_in"):
        return redirect("/login")

    base = Path(__file__).parent.parent
    fp = base / "templates" / "preview.html"

    if not fp.exists():
        return f"<h1>preview.html not found</h1><p>{fp}</p>", 404

    resp = send_file(fp)
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return resp
