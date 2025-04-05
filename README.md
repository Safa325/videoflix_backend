# 🎬 Videoflix Backend

A video processing and streaming backend built with **Django**, **Django REST Framework**, and **RQ (Redis Queue)** for asynchronous tasks like:

- 🔁 HLS conversion with `ffmpeg`
- 📸 Thumbnail generation
- 🎞️ Teaser video creation
- 🧠 Background status updates

Hosted on **Google Cloud Platform** and containerized using **Docker**.

---

## 🚀 Features

- Upload videos via Django Admin
- Automatically process and convert videos
- Generate multiple HLS resolutions
- Serve via HTTPS
- Integrates easily with Angular frontend

---

## 📦 Requirements

- Docker & Docker Compose
- Google Cloud instance (e.g. Compute Engine or Cloud Run)
- `.env` file with environment variables

---

## ⚙️ Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/videoflix-backend.git
cd videoflix-backend
```

### 2. Create a `.env` file

Here's an example `.env` file:

```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=videoflix.yourdomain.com,www.videoflix.yourdomain.com
DATABASE_URL=postgres://postgres:yourpassword@db:5432/postgres
REDIS_URL=redis://redis:6379
```

### 3. Build and run with Docker

```bash
docker-compose up --build
```

This will start:
- Django backend
- PostgreSQL database
- Redis
- RQ worker
- Nginx reverse proxy

### 4. Access Django Admin

Once running, visit:  
`https://videoflix.yourdomain.com/admin/`

The superuser is created automatically. You can customize this in the startup script (`entrypoint.prod.sh`).

---

## ☁️ Deploying to Google Cloud

- Deploy using Compute Engine with Docker
- Map your domain to the instance IP
- Use Certbot with Nginx for HTTPS
- Set up firewall rules for ports 80 and 443
- Configure persistent disk or volume mount for media files

---

## 🧪 API Endpoints

| Method | Endpoint                  | Description              |
|--------|---------------------------|--------------------------|
| GET    | `/api/videos/`            | List all videos          |
| POST   | `/api/videos/`            | Upload a new video       |
| GET    | `/api/videos/<slug>/`     | Get video details        |

---

## 🗂 Project Structure

```
videoflix-backend/
├── videos/               # App for video models, tasks & signals
├── userAuth/             # Auth system
├── media/                # Uploaded videos, HLS, thumbnails
├── static/               # Static assets
├── docker-compose.yml
├── entrypoint.prod.sh
└── .env
```

---

## 📄 License

This project is licensed under the MIT License.

---

## 🧠 Author

Built with ❤️ by [@shamarisafa](https://github.com/shamarisafa)
