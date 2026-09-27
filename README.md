# 🎬 MiniStream — Scalable Content Streaming Platform

A production-ready content streaming platform with microservices architecture, built with FastAPI, Flask, MySQL, MongoDB, Redis, and AWS S3.

## 🚀 Live Demo

- **Main API:** http://<EC2-IP>:8000
- **API Docs:** http://<EC2-IP>:8000/docs
- **Notification Service:** http://<EC2-IP>:5001

## 🏗️ Microservices Architecture

```
Client
    ↓
FastAPI Main API (Port 8000)
    ├── MySQL      → Users, Content, Subscriptions
    ├── MongoDB    → Comments, Analytics
    ├── Redis      → Trending, Views, Likes, Sessions, Feed Cache
    └── S3         → Videos, Images, Thumbnails

Flask Notification Service (Port 5001)
    └── Email/Push notifications

GitHub Actions → Docker Build → EC2 Auto-Deploy
```

## ✨ Features

| Feature            | Implementation                     |
| ------------------ | ---------------------------------- |
| User Auth          | JWT + bcrypt                       |
| Role System        | Creator / Viewer / Admin           |
| Content Upload     | AWS S3 (Video, Image, Article)     |
| Real-time Trending | Redis Sorted Set                   |
| View Tracking      | Redis + HyperLogLog (unique views) |
| Like System        | Redis Set (O(1) operations)        |
| Comments           | MongoDB (nested, soft delete)      |
| Subscriptions      | MySQL + Feed Cache                 |
| Search             | SQLAlchemy ilike + filters         |
| Analytics          | Creator stats + Platform stats     |
| Notifications      | Flask microservice                 |
| Caching            | Redis (feed, content, search)      |

## 🗄️ Why Multiple Databases?

| Data                          | Database | Why                          |
| ----------------------------- | -------- | ---------------------------- |
| Users, Content, Subscriptions | MySQL    | Structured, relational, ACID |
| Comments, Analytics logs      | MongoDB  | Flexible JSON, nested data   |
| Trending, Views, Likes, Cache | Redis    | Sub-millisecond speed        |
| Files (video, images)         | AWS S3   | Scalable, durable storage    |

## 📡 API Endpoints

### Auth

| Method | Endpoint                 | Auth | Description               |
| ------ | ------------------------ | ---- | ------------------------- |
| POST   | `/auth/signup`           | No   | Register (creator/viewer) |
| POST   | `/auth/login`            | No   | Login + JWT token         |
| GET    | `/auth/me`               | Yes  | My profile                |
| PUT    | `/auth/me`               | Yes  | Update profile            |
| GET    | `/auth/users/{username}` | No   | Public profile            |

### Content

| Method | Endpoint                | Auth    | Description                  |
| ------ | ----------------------- | ------- | ---------------------------- |
| POST   | `/content/upload`       | Creator | Upload content               |
| GET    | `/content/`             | No      | List published content       |
| GET    | `/content/{id}`         | No      | Get content + track view     |
| PUT    | `/content/{id}`         | Creator | Update own content           |
| DELETE | `/content/{id}`         | Creator | Delete + S3 cleanup          |
| POST   | `/content/{id}/publish` | Creator | Publish + notify subscribers |
| POST   | `/content/{id}/like`    | Yes     | Like/unlike toggle           |
| GET    | `/content/feed/me`      | Yes     | Personalized feed            |

### Subscriptions

| Method | Endpoint                        | Auth | Description        |
| ------ | ------------------------------- | ---- | ------------------ |
| POST   | `/subscriptions/follow/{id}`    | Yes  | Follow creator     |
| DELETE | `/subscriptions/unfollow/{id}`  | Yes  | Unfollow           |
| GET    | `/subscriptions/followers/{id}` | No   | Followers list     |
| GET    | `/subscriptions/following/{id}` | No   | Following list     |
| GET    | `/subscriptions/check/{id}`     | Yes  | Check if following |

### Trending & Search

| Method | Endpoint                   | Auth | Description          |
| ------ | -------------------------- | ---- | -------------------- |
| GET    | `/trending/`               | No   | Top trending content |
| GET    | `/trending/category/{cat}` | No   | Category trending    |
| GET    | `/search/content?q=...`    | No   | Search content       |
| GET    | `/search/creators?q=...`   | No   | Search creators      |
| GET    | `/search/categories`       | No   | All categories       |

### Comments

| Method | Endpoint                 | Auth | Description       |
| ------ | ------------------------ | ---- | ----------------- |
| GET    | `/comments/content/{id}` | No   | List comments     |
| POST   | `/comments/content/{id}` | Yes  | Add comment/reply |
| PUT    | `/comments/{id}`         | Yes  | Edit own comment  |
| DELETE | `/comments/{id}`         | Yes  | Soft delete       |
| POST   | `/comments/{id}/like`    | Yes  | Like/unlike       |

## 🚀 Setup

### Local Development

```bash
# Main API
cd main-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Notification Service (alag terminal)
cd notification-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app/main.py
```

### Docker (Recommended)

```bash
docker-compose up --build
```

### Tests

```bash
cd main-api
pytest tests/ -v
```

## 💡 Key Technical Decisions

### 1. Microservices

FastAPI (main) + Flask (notifications) — independently deployable, independently scalable.

### 2. Redis Data Structures

- **Sorted Set** → Trending leaderboard (real-time view ranking)
- **Set** → Likes (duplicate prevention, O(1) operations)
- **HyperLogLog** → Unique viewers (99% less memory vs Set)
- **String** → Sessions, feed cache

### 3. Denormalized Counts

`follower_count`, `views_count` stored in MySQL — fast reads without COUNT queries.

### 4. Soft Delete

Comments soft-deleted (`is_deleted: true`) — thread structure preserved.

### 5. Presigned URLs

S3 files private — temporary presigned URLs for secure access.

## 🔧 DevOps

- **Docker:** 5 containerized services
- **docker-compose:** One command deployment
- **GitHub Actions:** Auto-test + auto-deploy to EC2
- **systemd:** Auto-restart on server reboot

## 📈 What I Learned

- Microservices design and inter-service communication
- Redis advanced data structures for real-time features
- MongoDB aggregation for analytics
- AWS S3 presigned URLs for secure file access
- Multi-container Docker orchestration
- EC2 deployment with CI/CD auto-deploy
