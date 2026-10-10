# 📝 Django Blog System with Gemini AI

A dynamic blog management system built using **Python, Django, and Google Gemini AI**. The platform allows users to explore blog articles, manage content, and use AI-powered tools for article summarization and conversational assistance.

## 🚀 Features

### 📰 Blog Management
- Create, edit, and manage blog posts.
- Organize articles using categories.
- Display blog posts on the homepage.
- View individual blog articles.
- Support comments and reader engagement.
- Manage posts and categories through Django Admin.
- Support image uploads for blog content.

### 🤖 AI Blog Summarizer
- Generate concise summaries of blog articles using Google Gemini AI.
- Help readers understand lengthy articles more quickly.
- Integrate AI-powered summarization into the existing blog interface.

### 💬 AI Blog Chatbot
- Ask questions related to blog content.
- Receive conversational responses about available articles.
- Discover relevant posts through AI-assisted responses.
- Access the chatbot through its dedicated interface.

### 🛠️ Admin Panel
- Manage blog posts and categories.
- Manage users and comments.
- Edit and organize website content through Django's administrative interface.

### ☁️ Deployment
- Support for deployment on Render.
- Environment-variable configuration for API credentials.
- Static-file management using Django.
- Database configuration for local development and production.

---

## 🧰 Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Django | Backend web framework |
| HTML5 | Webpage structure |
| CSS3 | Styling and layout |
| JavaScript | Frontend interactions |
| Google Gemini API | AI summarization and chatbot |
| SQLite | Local development database |
| PostgreSQL | Production database option |
| Git and GitHub | Version control |
| Render | Cloud deployment |

Additional dependencies may include Pillow for image processing and Django Crispy Forms for form styling.

## 📂 Project Structure

```text
django-blog/
│
├── blog/
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── blog_main/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── static/
│
├── dashboards/
├── templates/
├── media/
├── manage.py
├── requirements.txt
└── README.md
```

*The structure above is illustrative; adjust it to match the actual files in your repository.*

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd django-blog
```

Replace the placeholder with your actual repository URL.

### 2. Create a virtual environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Configure the environment variables required by your project.

Example `.env` file:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True
GEMINI_API_KEY=your_gemini_api_key
```

Ensure your project loads these variables correctly. Never commit real API keys or production secrets to GitHub.

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Create an administrator account

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

Open:

`http://127.0.0.1:8000/`

Django Admin:

`http://127.0.0.1:8000/admin/`

## 🧠 AI Integration

### AI Blog Summarizer

The summarizer uses Google Gemini AI to generate a shorter version of a blog article. This helps readers identify the main ideas without reading the entire article first.

### AI Blog Chatbot

The chatbot provides a conversational interface for asking questions about blog content. Depending on its implementation, it can use available blog posts to help generate relevant responses.

Both AI features require valid API configuration and appropriate error handling.

## 🚀 Deployment on Render

A typical Django deployment uses the following configuration.

**Build command:**

```bash
pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate
```

**Start command:**

```bash
gunicorn blog_main.wsgi:application
```

Make sure Gunicorn is included in `requirements.txt` and that `blog_main` matches your Django project module.

Configure production environment variables:

- `SECRET_KEY`: a strong, private Django secret.
- `DEBUG`: set to `False`.
- `ALLOWED_HOSTS`: your deployed hostname.
- `GEMINI_API_KEY`: your Gemini API key.
- `DATABASE_URL`: your production database URL, if using PostgreSQL.
- `CSRF_TRUSTED_ORIGINS`: your trusted HTTPS website origin, when required.

Configure static and media storage appropriately. Uploaded files may require persistent or external storage on Render.

## 🔐 Security Best Practices

- Keep API keys and secret keys out of source control.
- Set `DEBUG=False` in production.
- Configure `ALLOWED_HOSTS` correctly.
- Use a persistent production database.
- Back up the database before production changes.
- Handle Gemini API failures gracefully.
- Validate and safely render user-generated content.
- Protect administrative operations with authentication and permissions.

## 🔮 Future Improvements

- SEO-friendly blog metadata.
- Improved article search and filtering.
- Rich-text editor and article previews.
- Enhanced AI responses based on relevant blog content.
- Better chatbot conversation history.
- Blog analytics and view tracking.
- Email notifications and improved user engagement.
- Support for additional languages.

## 👨‍💻 Project Overview

This project demonstrates the integration of a Django-based content management system with Generative AI. It combines web development, database management, API integration, and AI-powered features to improve the blogging experience.


**Built with Python, Django, and Google Gemini AI.**
## ⭐ Support

If you found this project useful, consider giving it a star ⭐ on GitHub.
