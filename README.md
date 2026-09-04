# 🎓 College Notice Hub

A centralized web application where students can view, search, and filter college
notices, and where an admin can add, edit, and delete them — built as a BE
Computer Science Engineering mini-project.

---

## 1. Project Overview

College Notice Hub replaces scattered physical notice boards and messages with a
single, searchable website. Students always know where to look for the latest
examination schedules, placement drives, events, and circulars.

## 2. Problem Statement

Colleges publish notices through multiple, disconnected channels — printed
notice boards, WhatsApp groups, email — making it easy for students to miss
important information. There is no single, searchable, always-available source
of truth.

## 3. Objective

- Provide one central place for all college notices.
- Let students search and filter notices by category instantly.
- Give the admin a simple dashboard to publish and manage notices.
- Support PDF and image attachments that can be viewed and downloaded directly
  in the browser.

## 4. Features

**Student side**
- View the latest notices on the home page.
- Browse notices by category (Examination, Internal Assessment, Placement,
  Events, Circular, Holidays, General).
- Search notices by title/description.
- Sort notices by newest or oldest.
- View a notice's full details, including an in-browser PDF viewer or image
  preview, plus a download button.

**Admin side**
- Secure login using hashed passwords (Werkzeug).
- Dashboard with live statistics (total notices, per-category counts).
- Add new notices with an attached PDF/image file.
- Edit existing notices, including replacing the attached file.
- Delete notices with a confirmation prompt.

## 5. Technologies Used

| Layer     | Technology                          |
|-----------|--------------------------------------|
| Frontend  | HTML5, CSS3, JavaScript, Bootstrap 5, Font Awesome |
| Backend   | Python 3, Flask                      |
| Database  | SQLite (via Python's built-in `sqlite3`) |
| Auth      | Flask sessions + Werkzeug password hashing |
| Dev Tools | VS Code, Python virtual environment  |

## 6. System Architecture

```
 ┌────────────┐      HTTP       ┌───────────────┐      SQL       ┌────────────┐
 │  Browser   │ <────────────>  │  Flask (app.py)│ <───────────> │  SQLite DB │
 │ (Bootstrap)│                 │  Routes/Views  │                │ database.db│
 └────────────┘                 └───────┬────────┘                └────────────┘
                                          │
                                          │ file save/serve
                                          ▼
                                 uploads/notices/*.pdf|.jpg|.png
```

- **Presentation layer:** Jinja2 templates + Bootstrap 5 + custom CSS/JS.
- **Application layer:** Flask routes handle requests, validation, and
  session-based admin authentication.
- **Data layer:** SQLite stores notice metadata and admin credentials; the
  actual files live on disk under `uploads/notices/`.

## 7. Database Structure

**`notices` table**

| Column          | Type    | Description                     |
|-----------------|---------|----------------------------------|
| id              | INTEGER | Primary key, auto-increment      |
| title           | TEXT    | Notice title                     |
| description     | TEXT    | Notice description               |
| category        | TEXT    | One of the 7 fixed categories     |
| filename        | TEXT    | Stored filename of the attachment |
| file_type       | TEXT    | `pdf`, `jpg`, `jpeg`, or `png`     |
| published_date  | TEXT    | Date shown to students (YYYY-MM-DD) |
| created_at      | TEXT    | Timestamp the row was created     |
| updated_at      | TEXT    | Timestamp of the last edit        |

**`admin` table**

| Column         | Type    | Description                  |
|----------------|---------|-------------------------------|
| id             | INTEGER | Primary key, auto-increment   |
| username       | TEXT    | Unique admin username         |
| password_hash  | TEXT    | Werkzeug-hashed password       |

## 8. Folder Structure

```
College-Notice-Hub/
│  app.py
│  create_admin.py
│  database.db          (created automatically on first run)
│  requirements.txt
│  README.md
│
├─templates/
│    base.html
│    index.html
│    notices.html
│    notice_details.html
│    about.html
│    admin_login.html
│    admin_dashboard.html
│    add_notice.html
│    edit_notice.html
│    404.html
│    500.html
│
├─static/
│  ├─css/style.css
│  ├─js/script.js
│  └─images/
│
└─uploads/
   └─notices/           (uploaded PDF/image files are stored here)
```

## 9. Installation

### Step 1 — Install Python
Download and install Python 3.10+ from https://python.org and make sure
**"Add Python to PATH"** is checked during installation.

### Step 2 — Open the project in VS Code
Unzip this project, then in VS Code: `File → Open Folder → College-Notice-Hub`.

### Step 3 — Create and activate a virtual environment
Open the VS Code terminal (`` Ctrl+` ``) and run:

```bash
python -m venv venv
```

Activate it:

```bash
# Windows PowerShell
venv\Scripts\Activate.ps1

# Windows Command Prompt
venv\Scripts\activate.bat
```

### Step 4 — Install dependencies

```bash
pip install -r requirements.txt
```

## 10. Admin Setup

Before logging in, create your first admin account:

```bash
python create_admin.py
```

You'll be prompted for a username and password in the terminal. The password
is hashed with Werkzeug before being stored — it is never saved as plain text.

## 11. Running the Application

```bash
python app.py
```

The first time you run `app.py`, it will automatically:
- Create `database.db`
- Create the `notices` and `admin` tables
- Insert 6 sample notices

Open your browser at: **http://127.0.0.1:5000**

## 12. How to Upload Notices

1. Go to `/admin/login` and sign in with the account you created.
2. Click **Add Notice** on the dashboard.
3. Fill in the title, description, category, and published date.
4. Attach a PDF, JPG, JPEG, or PNG file (max 5 MB).
5. Click **Publish Notice**.

## 13. How to Search Notices

Type a keyword into the search bar on the home page or the Notices page.
The search matches text in both the **title** and **description** fields, and
can be combined with a category filter and a newest/oldest sort order.

## 14. Future Enhancements

- Email/SMS notifications when a new notice is published.
- Multiple admin roles (super admin, department admin).
- Notice expiry dates and automatic archiving.
- Full-text search with ranking.
- Student bookmarking/favoriting of notices.
- REST API for a companion mobile app.

---

Built with Flask + SQLite as a college mini-project.
