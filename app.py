"""
College Notice Hub
A Flask + SQLite mini-project that lets students browse college notices
and lets an admin add / edit / delete them.

Run with: python app.py
"""

import os
import sqlite3
from datetime import datetime, date

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, send_from_directory, abort, g
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


# --------------------------------------------------------------------------
# APP CONFIGURATION
# --------------------------------------------------------------------------

app = Flask(__name__)

app.config["SECRET_KEY"] = "change-this-secret-key-in-production"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "notices")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Maximum upload size = 20 MB
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

CATEGORIES = [
    "Examination",
    "Internal Assessment",
    "Placement",
    "Events",
    "Circular",
    "Holidays",
    "General",
]

CATEGORY_ICONS = {
    "Examination": "📚",
    "Internal Assessment": "📝",
    "Placement": "💼",
    "Events": "🎉",
    "Circular": "📢",
    "Holidays": "🏖",
    "General": "📌",
}


# --------------------------------------------------------------------------
# DATABASE HELPERS
# --------------------------------------------------------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create database tables and default admin account."""

    db = sqlite3.connect(DATABASE)

    # Notices table
    db.execute("""
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            filename TEXT,
            file_type TEXT,
            published_date TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # Admin table
    db.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    # Create default admin account
    admin_exists = db.execute(
        "SELECT id FROM admin WHERE username = ?",
        ("admin",)
    ).fetchone()

    if admin_exists is None:
        password_hash = generate_password_hash("admin123")

        db.execute(
            "INSERT INTO admin (username, password_hash) VALUES (?, ?)",
            ("admin", password_hash)
        )

    db.commit()
    db.close()


def insert_sample_data():
    """Insert sample notices if database is empty."""

    db = sqlite3.connect(DATABASE)

    count = db.execute(
        "SELECT COUNT(*) FROM notices"
    ).fetchone()[0]

    if count == 0:

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        samples = [
            (
                "Semester Examination Schedule",
                "The schedule for the upcoming semester end examinations has been released.",
                "Examination",
                None,
                None,
                "2026-09-01",
                now,
                now,
            ),
            (
                "Internal Assessment III Notice",
                "Internal Assessment III for all branches will be conducted next week.",
                "Internal Assessment",
                None,
                None,
                "2026-08-28",
                now,
                now,
            ),
            (
                "Placement Drive Announcement",
                "A campus placement drive is being organized for eligible students.",
                "Placement",
                None,
                None,
                "2026-08-25",
                now,
                now,
            ),
            (
                "College Annual Day",
                "The college Annual Day celebrations will be held in the main auditorium.",
                "Events",
                None,
                None,
                "2026-08-20",
                now,
                now,
            ),
            (
                "Holiday Notice",
                "The college will remain closed on account of a regional holiday.",
                "Holidays",
                None,
                None,
                "2026-08-15",
                now,
                now,
            ),
            (
                "General Circular",
                "All students are informed to update their contact details.",
                "General",
                None,
                None,
                "2026-08-10",
                now,
                now,
            ),
        ]

        db.executemany(
            """
            INSERT INTO notices
            (
                title,
                description,
                category,
                filename,
                file_type,
                published_date,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            samples
        )

        db.commit()

    db.close()


# --------------------------------------------------------------------------
# UTILITY FUNCTIONS
# --------------------------------------------------------------------------

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def login_required(view_func):

    from functools import wraps

    @wraps(view_func)
    def wrapped_view(*args, **kwargs):

        if not session.get("admin_logged_in"):
            flash(
                "Please login to access the admin area.",
                "error"
            )

            return redirect(url_for("admin_login"))

        return view_func(*args, **kwargs)

    return wrapped_view


def format_date_for_display(date_str):

    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return d.strftime("%d %B %Y")

    except (ValueError, TypeError):
        return date_str


@app.context_processor
def inject_globals():

    return {
        "categories": CATEGORIES,
        "category_icons": CATEGORY_ICONS,
        "format_date": format_date_for_display,
        "current_year": date.today().year,
    }


# --------------------------------------------------------------------------
# PUBLIC ROUTES
# --------------------------------------------------------------------------

@app.route("/")
def index():

    db = get_db()

    latest_notices = db.execute(
        """
        SELECT *
        FROM notices
        ORDER BY published_date DESC, id DESC
        LIMIT 6
        """
    ).fetchall()

    return render_template(
        "index.html",
        notices=latest_notices
    )


@app.route("/notices")
def notices():

    db = get_db()

    search_query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    sort_order = request.args.get("sort", "newest")

    sql = "SELECT * FROM notices WHERE 1=1"
    params = []

    if search_query:

        sql += """
            AND (
                title LIKE ?
                OR description LIKE ?
            )
        """

        like_term = f"%{search_query}%"

        params.extend([
            like_term,
            like_term
        ])

    if category and category in CATEGORIES:

        sql += " AND category = ?"
        params.append(category)

    if sort_order == "oldest":

        sql += """
            ORDER BY published_date ASC, id ASC
        """

    else:

        sql += """
            ORDER BY published_date DESC, id DESC
        """

    all_notices = db.execute(
        sql,
        params
    ).fetchall()

    return render_template(
        "notices.html",
        notices=all_notices,
        search_query=search_query,
        selected_category=category,
        sort_order=sort_order,
    )


@app.route("/notice/<int:notice_id>")
def notice_details(notice_id):

    db = get_db()

    notice = db.execute(
        "SELECT * FROM notices WHERE id = ?",
        (notice_id,)
    ).fetchone()

    if notice is None:
        abort(404)

    return render_template(
        "notice_details.html",
        notice=notice
    )


@app.route("/about")
def about():

    return render_template("about.html")


@app.route("/uploads/notices/<path:filename>")
def uploaded_file(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


# --------------------------------------------------------------------------
# ADMIN AUTH ROUTES
# --------------------------------------------------------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        db = get_db()

        admin = db.execute(
            "SELECT * FROM admin WHERE username = ?",
            (username,)
        ).fetchone()

        if admin and check_password_hash(
            admin["password_hash"],
            password
        ):

            session["admin_logged_in"] = True
            session["admin_username"] = admin["username"]

            flash(
                "Logged in successfully.",
                "success"
            )

            return redirect(
                url_for("admin_dashboard")
            )

        else:

            flash(
                "Invalid username or password.",
                "error"
            )

    return render_template(
        "admin_login.html"
    )


@app.route("/admin/logout")
def admin_logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("admin_login")
    )


# --------------------------------------------------------------------------
# ADMIN DASHBOARD
# --------------------------------------------------------------------------

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():

    db = get_db()

    total_notices = db.execute(
        "SELECT COUNT(*) FROM notices"
    ).fetchone()[0]

    def count_for(cat):

        return db.execute(
            """
            SELECT COUNT(*)
            FROM notices
            WHERE category = ?
            """,
            (cat,)
        ).fetchone()[0]

    stats = {
        "total": total_notices,
        "examination": count_for("Examination"),
        "placement": count_for("Placement"),
        "events": count_for("Events"),
        "internal_assessment": count_for(
            "Internal Assessment"
        ),
    }

    recent_notices = db.execute(
        """
        SELECT *
        FROM notices
        ORDER BY created_at DESC
        LIMIT 8
        """
    ).fetchall()

    return render_template(
        "admin_dashboard.html",
        stats=stats,
        notices=recent_notices
    )


# --------------------------------------------------------------------------
# ADD NOTICE
# --------------------------------------------------------------------------

@app.route("/admin/add", methods=["GET", "POST"])
@login_required
def add_notice():

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        published_date = request.form.get(
            "published_date",
            ""
        ).strip()

        file = request.files.get(
            "notice_file"
        )

        # Basic validation
        if not title or not description or not category or not published_date:

            flash(
                "Please fill in all required fields.",
                "error"
            )

            return render_template(
                "add_notice.html"
            )

        if category not in CATEGORIES:

            flash(
                "Please choose a valid category.",
                "error"
            )

            return render_template(
                "add_notice.html"
            )

        filename = None
        file_type = None

        # --------------------------------------------------------------
        # FILE UPLOAD
        # --------------------------------------------------------------

        if file and file.filename:

            if not allowed_file(file.filename):

                flash(
                    "Please upload a valid file (PDF, PNG, JPG, JPEG).",
                    "error"
                )

                return render_template(
                    "add_notice.html"
                )

            original_name = secure_filename(
                file.filename
            )

            # Fix duplicate .pdf.pdf
            while original_name.lower().endswith(".pdf.pdf"):

                original_name = original_name[:-4]

            file_type = original_name.rsplit(
                ".",
                1
            )[1].lower()

            timestamp = datetime.now().strftime(
                "%Y%m%d%H%M%S%f"
            )

            filename = f"{timestamp}_{original_name}"

            # Create uploads/notices folder
            os.makedirs(
                app.config["UPLOAD_FOLDER"],
                exist_ok=True
            )

            # Save uploaded file
            file.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        # --------------------------------------------------------------
        # SAVE NOTICE TO DATABASE
        # --------------------------------------------------------------

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        db = get_db()

        db.execute(
            """
            INSERT INTO notices
            (
                title,
                description,
                category,
                filename,
                file_type,
                published_date,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                description,
                category,
                filename,
                file_type,
                published_date,
                now,
                now
            )
        )

        db.commit()

        flash(
            "Notice published successfully.",
            "success"
        )

        return redirect(
            url_for("admin_dashboard")
        )

    return render_template(
        "add_notice.html"
    )


# --------------------------------------------------------------------------
# EDIT NOTICE
# --------------------------------------------------------------------------

@app.route("/admin/edit/<int:notice_id>", methods=["GET", "POST"])
@login_required
def edit_notice(notice_id):

    db = get_db()

    notice = db.execute(
        "SELECT * FROM notices WHERE id = ?",
        (notice_id,)
    ).fetchone()

    if notice is None:
        abort(404)

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        published_date = request.form.get(
            "published_date",
            ""
        ).strip()

        file = request.files.get(
            "notice_file"
        )

        if not title or not description or not category or not published_date:

            flash(
                "Please fill in all required fields.",
                "error"
            )

            return render_template(
                "edit_notice.html",
                notice=notice
            )

        if category not in CATEGORIES:

            flash(
                "Please choose a valid category.",
                "error"
            )

            return render_template(
                "edit_notice.html",
                notice=notice
            )

        filename = notice["filename"]
        file_type = notice["file_type"]

        # New file uploaded
        if file and file.filename:

            if not allowed_file(file.filename):

                flash(
                    "Please upload a valid file (PDF, PNG, JPG, JPEG).",
                    "error"
                )

                return render_template(
                    "edit_notice.html",
                    notice=notice
                )

            # Delete old file
            if filename:

                old_path = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )

                if os.path.exists(old_path):
                    os.remove(old_path)

            original_name = secure_filename(
                file.filename
            )

            while original_name.lower().endswith(".pdf.pdf"):

                original_name = original_name[:-4]

            file_type = original_name.rsplit(
                ".",
                1
            )[1].lower()

            timestamp = datetime.now().strftime(
                "%Y%m%d%H%M%S%f"
            )

            filename = f"{timestamp}_{original_name}"

            os.makedirs(
                app.config["UPLOAD_FOLDER"],
                exist_ok=True
            )

            file.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        db.execute(
            """
            UPDATE notices
            SET
                title = ?,
                description = ?,
                category = ?,
                filename = ?,
                file_type = ?,
                published_date = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                title,
                description,
                category,
                filename,
                file_type,
                published_date,
                now,
                notice_id
            )
        )

        db.commit()

        flash(
            "Notice updated successfully.",
            "success"
        )

        return redirect(
            url_for("admin_dashboard")
        )

    return render_template(
        "edit_notice.html",
        notice=notice
    )


# --------------------------------------------------------------------------
# DELETE NOTICE
# --------------------------------------------------------------------------

@app.route("/admin/delete/<int:notice_id>", methods=["POST"])
@login_required
def delete_notice(notice_id):

    db = get_db()

    notice = db.execute(
        "SELECT * FROM notices WHERE id = ?",
        (notice_id,)
    ).fetchone()

    if notice is None:
        abort(404)

    if notice["filename"]:

        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            notice["filename"]
        )

        if os.path.exists(file_path):
            os.remove(file_path)

    db.execute(
        "DELETE FROM notices WHERE id = ?",
        (notice_id,)
    )

    db.commit()

    flash(
        "Notice deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin_dashboard")
    )


# --------------------------------------------------------------------------
# ERROR HANDLERS
# --------------------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(e):

    return render_template(
        "404.html"
    ), 404


@app.errorhandler(500)
def server_error(e):

    return render_template(
        "500.html"
    ), 500


@app.errorhandler(413)
def file_too_large(e):

    flash(
        "The uploaded file is too large. Maximum size is 20 MB.",
        "error"
    )

    return redirect(
        request.referrer or url_for("index")
    )


# --------------------------------------------------------------------------
# APP ENTRY POINT
# --------------------------------------------------------------------------

if __name__ == "__main__":

    os.makedirs(
        app.config["UPLOAD_FOLDER"],
        exist_ok=True
    )

    init_db()
    insert_sample_data()

    app.run(
        debug=True
    )

