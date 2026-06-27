import os
import secrets
import asyncio
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, session, flash, jsonify,
)
from dotenv import load_dotenv
import web_db

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))

ADMIN_USER = os.getenv("ADMIN_WEB_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_WEB_PASS", "changeme")


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == ADMIN_USER and password == ADMIN_PASS:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        user_count=web_db.get_user_count(),
        config_count=web_db.get_config_count(),
        revenue=web_db.get_total_revenue(),
        pending=web_db.get_pending_receipt_count(),
        symbol=web_db.get_setting("currency_symbol") or "تومان",
    )


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        for key in request.form:
            if key.startswith("_"):
                continue
            web_db.set_setting(key, request.form[key])
        from api import panel_api
        panel_api.reload_config()
        flash("Settings saved successfully!", "success")
        return redirect(url_for("settings"))
    all_settings = web_db.get_all_settings()
    return render_template("settings.html", settings=all_settings)


@app.route("/api/inbounds")
@login_required
def api_inbounds():
    from api import panel_api
    panel_api.reload_config()
    if not panel_api.panel_url or not panel_api.panel_user:
        return jsonify([])
    try:
        loop = asyncio.new_event_loop()
        inbounds = loop.run_until_complete(panel_api.get_inbounds())
        loop.close()
        result = [{"id": i["id"], "protocol": i.get("protocol", ""), "tag": i.get("tag", ""), "enable": i.get("enable", False)} for i in inbounds]
        return jsonify(result)
    except Exception as e:
        return jsonify([])


@app.route("/plans")
@login_required
def plans():
    return render_template(
        "plans.html",
        plans=web_db.get_all_plans(),
        symbol=web_db.get_setting("currency_symbol") or "تومان",
    )


@app.route("/plans/add", methods=["GET", "POST"])
@login_required
def plan_add():
    if request.method == "POST":
        name = request.form["name"]
        gb = int(request.form["gb"])
        days = int(request.form["days"])
        price = int(request.form["price"])
        web_db.add_plan(name, gb, days, price)
        flash(f"Plan '{name}' added!", "success")
        return redirect(url_for("plans"))
    return render_template("plan_form.html", plan=None)


@app.route("/plans/<int:plan_id>/edit", methods=["GET", "POST"])
@login_required
def plan_edit(plan_id):
    plan = web_db.get_plan(plan_id)
    if not plan:
        flash("Plan not found", "danger")
        return redirect(url_for("plans"))
    if request.method == "POST":
        web_db.update_plan(
            plan_id,
            name=request.form["name"],
            gb=int(request.form["gb"]),
            days=int(request.form["days"]),
            price=int(request.form["price"]),
            is_active="is_active" in request.form,
        )
        flash(f"Plan '{request.form['name']}' updated!", "success")
        return redirect(url_for("plans"))
    return render_template("plan_form.html", plan=plan)


@app.route("/plans/<int:plan_id>/delete", methods=["POST"])
@login_required
def plan_delete(plan_id):
    web_db.delete_plan(plan_id)
    flash("Plan deleted", "success")
    return redirect(url_for("plans"))


@app.route("/users")
@login_required
def users():
    search = request.args.get("q", "").strip() or None
    return render_template("users.html", users=web_db.get_all_users(search), search=search)


@app.route("/users/<int:user_id>")
@login_required
def user_detail(user_id):
    user = web_db.get_user(user_id)
    if not user:
        flash("User not found", "danger")
        return redirect(url_for("users"))
    configs = web_db.get_user_configs(user_id)
    symbol = web_db.get_setting("currency_symbol") or "تومان"
    return render_template("user_detail.html", user=user, configs=configs, symbol=symbol)


@app.route("/users/<int:user_id>/balance", methods=["POST"])
@login_required
def user_balance(user_id):
    action = request.form["action"]
    try:
        amount = float(request.form["amount"])
    except (ValueError, KeyError):
        flash("Invalid amount", "danger")
        return redirect(url_for("user_detail", user_id=user_id))
    if action == "add":
        web_db.update_balance(user_id, amount)
        flash(f"Added {amount:,.0f}", "success")
    elif action == "remove":
        user = web_db.get_user(user_id)
        if user and user["balance"] >= amount:
            web_db.update_balance(user_id, -amount)
            flash(f"Removed {amount:,.0f}", "success")
        else:
            flash("Insufficient balance", "danger")
    return redirect(url_for("user_detail", user_id=user_id))


@app.route("/users/<int:user_id>/ban", methods=["POST"])
@login_required
def user_ban(user_id):
    user = web_db.get_user(user_id)
    if user:
        new_status = not bool(user["is_banned"])
        web_db.set_banned(user_id, new_status)
        flash("User unbanned" if not new_status else "User banned", "success")
    return redirect(url_for("user_detail", user_id=user_id))


@app.route("/receipts")
@login_required
def receipts():
    status_filter = request.args.get("status", "pending")
    if status_filter == "all":
        receipts_list = web_db.get_receipts(limit=100)
    else:
        receipts_list = web_db.get_receipts(status=status_filter, limit=100)
    symbol = web_db.get_setting("currency_symbol") or "تومان"
    return render_template("receipts.html", receipts=receipts_list, status=status_filter, symbol=symbol)


@app.route("/receipts/<int:receipt_id>/approve", methods=["POST"])
@login_required
def receipt_approve(receipt_id):
    web_db.approve_receipt(receipt_id)
    flash(f"Receipt #{receipt_id} approved!", "success")
    return redirect(url_for("receipts"))


@app.route("/receipts/<int:receipt_id>/reject", methods=["POST"])
@login_required
def receipt_reject(receipt_id):
    web_db.reject_receipt(receipt_id)
    flash(f"Receipt #{receipt_id} rejected", "warning")
    return redirect(url_for("receipts"))


@app.route("/configs")
@login_required
def configs():
    configs_list = web_db.get_all_configs()
    symbol = web_db.get_setting("currency_symbol") or "تومان"
    return render_template("configs.html", configs=configs_list, symbol=symbol)


@app.route("/configs/<int:config_id>/delete", methods=["POST"])
@login_required
def config_delete(config_id):
    web_db.delete_config(config_id)
    flash("Config deleted", "success")
    return redirect(url_for("configs"))


@app.route("/configs/<int:config_id>/deactivate", methods=["POST"])
@login_required
def config_deactivate(config_id):
    web_db.deactivate_config(config_id)
    flash("Config deactivated", "warning")
    return redirect(url_for("configs"))


@app.route("/admins")
@login_required
def admins():
    return render_template("admins.html", admins=web_db.get_admins())


@app.route("/admins/add", methods=["POST"])
@login_required
def admin_add():
    try:
        user_id = int(request.form["user_id"])
    except (ValueError, KeyError):
        flash("Invalid user ID", "danger")
        return redirect(url_for("admins"))
    username = request.form.get("username") or None
    web_db.add_admin(user_id, username)
    flash(f"Admin {user_id} added!", "success")
    return redirect(url_for("admins"))


@app.route("/admins/<int:user_id>/remove", methods=["POST"])
@login_required
def admin_remove(user_id):
    web_db.remove_admin(user_id)
    flash(f"Admin {user_id} removed", "success")
    return redirect(url_for("admins"))


@app.route("/broadcast", methods=["GET", "POST"])
@login_required
def broadcast():
    if request.method == "POST":
        text = request.form.get("message", "").strip()
        if not text:
            flash("Message cannot be empty", "danger")
            return redirect(url_for("broadcast"))
        import sqlite3
        from config import DB_PATH
        conn = sqlite3.connect(DB_PATH)
        users = conn.execute("SELECT id FROM users").fetchall()
        conn.close()
        count = len(users)
        flash(f"Broadcast prepared for {count} users. Use the Telegram bot /admin > Broadcast to send.", "info")
        return redirect(url_for("broadcast"))
    return render_template("broadcast.html")


if __name__ == "__main__":
    port = int(os.getenv("WEB_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
