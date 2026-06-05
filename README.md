### 📝 Django Blog

A modern blog web application built using **Django** and **Bootstrap**. Users can register, create blog posts, manage their content, interact through comments, and access a personalized dashboard.

### 🚀 Features

  Authentication
- User Registration
- User Login
- User Logout

### Blog Management
- Create Blog Posts
- Read Blog Posts
- Update Existing Posts
- Delete Posts

### User Dashboard
- Manage Personal Posts
- View User Activity
- Personalized Dashboard Interface

### Comment System
- Add Comments on Posts
- View Comments

### UI & Design
- Responsive Bootstrap Design
- Mobile-Friendly Layout
- Clean and Modern Interface

---

## 🛠 Tech Stack

| Technology | Purpose |
|------------|----------|
| Python | Programming Language |
| Django | Backend Framework |
| Bootstrap | Frontend Framework |
| HTML/CSS | UI Development |
| SQLite | Database |

---

## 📂 Project Structure

```text
django-blog/
│
├── blog/
├── blog_main/
├── dashboards/
├── templates/
├── manage.py
├── requirements.txt
├── db.sqlite3
└── .gitignore
```

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/atharvtambe/django-blog.git
cd django-blog
```

### Create Virtual Environment

```bash
python -m venv env
```

### Activate Virtual Environment

Windows:

```bash
env\Scripts\activate
```

Linux/Mac:

```bash
source env/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Migrations

```bash
python manage.py migrate
```

### Start Development Server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

## 🔑 Admin Panel

Create a superuser:

```bash
python manage.py createsuperuser
```

Access:

```text
http://127.0.0.1:8000/admin/
```

---

## 🎯 Future Improvements

- User Profile Pictures
- Post Categories & Tags
- Rich Text Editor
- Search Functionality
- Like System
- REST API Integration
- Deployment on AWS/Render

---

## 📸 Screenshots

Add screenshots of:
- Home Page
- Blog Detail Page
- Dashboard
- Login/Register Page

---

## 👨‍💻 Author

**Atharv Tambe**

GitHub: https://github.com/atharvtambe

---

## ⭐ Support

If you found this project useful, consider giving it a star ⭐ on GitHub.
