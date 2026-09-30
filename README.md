# 🎬 MiniStream — Content Streaming Platform

A production-style content streaming platform backend built with **FastAPI, Flask, MySQL, MongoDB, Redis, AWS S3, Docker, and GitHub Actions**.

MiniStream uses a microservices architecture where the FastAPI application handles the main platform APIs and a separate Flask service handles notifications.

## 🚀 Live Demo

**Frontend:**
https://novus-one-eta.vercel.app

**Main API:**
https://ministream-main-app.onrender.com

**API Documentation:**
https://ministream-main-app.onrender.com/docs

**Notification Service:**
https://ministream-notification.onrender.com

## 🔗 Repositories

**Backend:**
https://github.com/ratneshbuilds03/ministream06

**Frontend:**
https://github.com/ratneshbuilds03/ministream-frontend

## 🏗️ Microservices Architecture

```text
Client
   │
   ▼
FastAPI Main API
   │
   ├── MySQL
   │      └── Users, Content, Subscriptions
   │
   ├── MongoDB
   │      └── Comments, Analytics
   │
   ├── Redis
   │      └── Trending, Views, Likes, Sessions, Cache
   │
   └── AWS S3
          └── Videos, Images, Thumbnails

FastAPI Main API
   │
   ▼
Flask Notification Service
   └── Subscriber Notifications
```

## ✨ Features

* User registration and login
* JWT-based authentication
* Role-based access for creators and viewers
* Creator content upload
* Video, image, and article content support
* AWS S3 file storage
* Presigned URLs for content access
* Content publishing workflow
* Content view tracking
* Like/unlike functionality
* Real-time trending content
* Personalized content feed
* Creator subscriptions
* Content search
* Creator search
* Category-based search
* Nested comments and replies
* Comment editing
* Soft deletion of comments
* Comment likes
* Creator and platform analytics
* Redis caching
* Notification microservice
* Dockerized services
* Automated backend testing
* GitHub Actions CI pipeline

## 🛠️ Tech Stack

* **Python**
* **FastAPI**
* **Flask**
* **SQLAlchemy**
* **MySQL**
* **MongoDB**
* **Redis**
* **AWS S3**
* **JWT**
* **bcrypt**
* **Docker**
* **Docker Compose**
* **GitHub Actions**
* **Render**
* **Vercel**

## 🗄️ Database Architecture

MiniStream uses different storage technologies based on the type of data being handled.

| Data             | Technology | Purpose                            |
| ---------------- | ---------- | ---------------------------------- |
| Users            | MySQL      | Relational user data               |
| Content metadata | MySQL      | Structured content information     |
| Subscriptions    | MySQL      | Creator subscription relationships |
| Comments         | MongoDB    | Flexible nested comment data       |
| Analytics        | MongoDB    | Analytics and event-oriented data  |
| Trending         | Redis      | Fast ranking operations            |
| Views            | Redis      | View tracking                      |
| Likes            | Redis      | Fast like/unlike operations        |
| Sessions / Cache | Redis      | Temporary and cached data          |
| Videos / Images  | AWS S3     | File and media storage             |

## 🔐 Authentication

MiniStream uses JWT-based authentication.

### Signup

```http
POST /auth/signup
```

Creates a new user account.

### Login

```http
POST /auth/login
```

Authenticates the user and returns an access token.

### Current User

```http
GET /auth/me
```

Returns the authenticated user's profile.

### Public Profile

```http
GET /auth/users/{username}
```

Returns a user's public profile.

## 📡 API Endpoints

### Authentication

| Method | Endpoint                 | Auth | Description           |
| ------ | ------------------------ | ---- | --------------------- |
| POST   | `/auth/signup`           | No   | Register a user       |
| POST   | `/auth/login`            | No   | Login and receive JWT |
| GET    | `/auth/me`               | Yes  | Get current user      |
| PUT    | `/auth/me`               | Yes  | Update profile        |
| GET    | `/auth/users/{username}` | No   | Get public profile    |

### Content

| Method | Endpoint                | Auth    | Description                |
| ------ | ----------------------- | ------- | -------------------------- |
| POST   | `/content/upload`       | Creator | Upload content             |
| GET    | `/content/`             | No      | List published content     |
| GET    | `/content/{id}`         | No      | Get content and track view |
| PUT    | `/content/{id}`         | Creator | Update own content         |
| DELETE | `/content/{id}`         | Creator | Delete content             |
| POST   | `/content/{id}/publish` | Creator | Publish content            |
| POST   | `/content/{id}/like`    | Yes     | Like/unlike content        |
| GET    | `/content/feed/me`      | Yes     | Get personalized feed      |

### Subscriptions

| Method | Endpoint                        | Auth | Description        |
| ------ | ------------------------------- | ---- | ------------------ |
| POST   | `/subscriptions/follow/{id}`    | Yes  | Follow creator     |
| DELETE | `/subscriptions/unfollow/{id}`  | Yes  | Unfollow creator   |
| GET    | `/subscriptions/followers/{id}` | No   | Get followers      |
| GET    | `/subscriptions/following/{id}` | No   | Get following list |
| GET    | `/subscriptions/check/{id}`     | Yes  | Check subscription |

### Trending & Search

| Method | Endpoint                   | Auth | Description           |
| ------ | -------------------------- | ---- | --------------------- |
| GET    | `/trending/`               | No   | Get trending content  |
| GET    | `/trending/category/{cat}` | No   | Get category trending |
| GET    | `/search/content?q=...`    | No   | Search content        |
| GET    | `/search/creators?q=...`   | No   | Search creators       |
| GET    | `/search/categories`       | No   | List categories       |

### Comments

| Method | Endpoint                 | Auth | Description         |
| ------ | ------------------------ | ---- | ------------------- |
| GET    | `/comments/content/{id}` | No   | Get comments        |
| POST   | `/comments/content/{id}` | Yes  | Add comment/reply   |
| PUT    | `/comments/{id}`         | Yes  | Edit own comment    |
| DELETE | `/comments/{id}`         | Yes  | Soft delete comment |
| POST   | `/comments/{id}/like`    | Yes  | Like/unlike comment |

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/ratneshbuilds03/ministream06.git
cd ministream06
```

### 2. Main API setup

```powershell
cd main-app
python -m venv venv
```

Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

### 3. Notification Service

Open another terminal:

```powershell
cd notification-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Start the notification service:

```powershell
python app/main.py
```

### 4. Start the Main API

From the `main-app` directory:

```powershell
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## 🐳 Docker Setup

MiniStream includes Docker configuration for the main application and supporting services.

Build and start the services with:

```bash
docker compose up --build
```

The Docker environment includes the main application, notification service, MySQL, MongoDB, and Redis services according to the project configuration.

## 🧪 Testing

The backend includes automated tests covering authentication, content, search, subscriptions, and related application functionality.

Run the test suite from `main-app`:

```powershell
cd main-app
pytest
```

## 💡 Key Technical Decisions

### 1. Microservices Architecture

The main platform API is built with FastAPI while notifications are handled by a separate Flask service.

This keeps notification functionality separated from the core application.

### 2. Redis Data Structures

Redis is used for high-speed operations such as:

* Trending content
* View tracking
* Likes
* Sessions
* Feed caching

### 3. Multiple Database Technologies

MySQL handles structured relational data while MongoDB handles flexible document-oriented data. Redis is used for fast temporary and frequently accessed data.

### 4. Presigned S3 URLs

Media files are stored in AWS S3 and accessed through temporary presigned URLs instead of exposing direct storage access.

### 5. Role-Based Access

Different application roles provide different capabilities, including creator-specific content operations.

## 🔄 Content Flow

```text
Creator
   │
   ▼
Upload Content
   │
   ▼
AWS S3 Storage
   │
   ▼
Content Metadata
   │
   ▼
Publish
   │
   ├── Subscriber Notification
   │
   └── Content Available
             │
             ▼
          View / Like
             │
             ▼
        Redis Tracking
```

## 🔄 Development & Deployment

```text
Developer
    │
    ▼
GitHub Repository
    │
    ▼
GitHub Actions
    │
    ├── Install Dependencies
    ├── Run Tests
    └── CI Validation
    │
    ▼
Docker
    │
    ▼
Deployment
    │
    ├── Render Main API
    └── Render Notification Service
```

## 🌐 Deployment

The MiniStream backend is deployed using **Render**.

### Main API

https://ministream-main-app.onrender.com

### API Documentation

https://ministream-main-app.onrender.com/docs

### Notification Service

https://ministream-notification.onrender.com

The frontend is deployed separately using Vercel.

### Frontend

https://novus-one-eta.vercel.app

## 🔑 Environment Variables

The application uses environment variables for database connections, authentication, AWS services, Redis, and notification service configuration.

Example:

```env
DATABASE_URL=your_mysql_database_url
MONGODB_URL=your_mongodb_connection_string
MONGODB_DB=ministream_db
REDIS_URL=your_redis_url
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_BUCKET_NAME=your_bucket_name
AWS_REGION=ap-south-1

NOTIFICATION_SERVICE_URL=http://localhost:5001
```

**Never commit real credentials, AWS keys, database passwords, or secret keys to GitHub.**

## 📁 Project Structure

```text
ministream06/
│
├── main-app/
│   ├── app/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── models/
│   │   └── main.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── pytest.ini
│
├── notification-service/
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml
├── Dockerfile
├── .dockerignore
└── README.md
```

## 📈 What I Learned

* Designing microservices with FastAPI and Flask
* Working with multiple databases in one application
* Using Redis data structures for high-speed operations
* Implementing JWT authentication and role-based access
* Integrating AWS S3 for media storage
* Generating presigned URLs for private files
* Building REST APIs with FastAPI
* Writing automated backend tests with Pytest
* Containerizing applications with Docker
* Using GitHub Actions for CI
* Deploying backend services to a cloud platform

## 🔮 Future Improvements

* Video streaming optimization
* Advanced recommendation system
* More detailed creator analytics
* Improved notification delivery
* Content moderation tools
* Admin dashboard
* Advanced search and filtering
* Automated production monitoring

## 📄 License

This project is created for educational, portfolio, and placement purposes.
