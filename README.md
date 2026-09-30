# Cartify Backend 🛒

A production-style e-commerce backend built with **FastAPI**, **MySQL**, **MongoDB**, **JWT authentication**, and **Docker**.

The backend provides authentication, product management, cart management, checkout, and order functionality for the Cartify frontend.

## 🚀 Live API

**Backend:**
https://cart-system-ylj0.onrender.com

**Swagger / OpenAPI Documentation:**
https://cart-system-ylj0.onrender.com/docs

**Frontend:**
https://cartify-pi-nine.vercel.app/

---

## ✨ Features

* User registration and login
* JWT-based authentication
* Protected API endpoints
* Product management
* Product image support
* MongoDB product storage
* Shopping cart management
* Checkout and order placement
* MySQL user and order data
* MongoDB product and cart data
* CORS configuration for production frontend
* API validation using Pydantic
* Dockerized application
* Production deployment on Render
* Interactive Swagger API documentation

---

## 🛠️ Tech Stack

| Technology               | Purpose                |
| ------------------------ | ---------------------- |
| FastAPI                  | Backend REST API       |
| Python                   | Backend development    |
| MySQL                    | Users and orders       |
| MongoDB                  | Products and cart data |
| SQLAlchemy               | MySQL ORM              |
| PyMongo / MongoDB Driver | MongoDB integration    |
| Pydantic                 | Data validation        |
| JWT                      | Authentication         |
| Docker                   | Containerization       |
| Render                   | Backend deployment     |
| Vercel                   | Frontend deployment    |

---

## 🏗️ Architecture

Cartify uses a **dual-database architecture**.

### MySQL

Used for relational data such as:

* Users
* Orders
* Authentication-related data

### MongoDB

Used for flexible e-commerce data such as:

* Products
* Shopping cart data

This separation allows relational and document-based data to be handled according to their respective use cases.

---

## 🔐 Authentication

Cartify uses **JWT-based authentication**.

### Authentication Flow

```text
User
 │
 ├── Signup
 │
 ▼
FastAPI
 │
 ├── Validate User Data
 ├── Create User
 │
 ▼
MySQL
```

For login:

```text
User Login
    │
    ▼
FastAPI
    │
    ├── Validate Credentials
    │
    ▼
JWT Token
    │
    ▼
Authenticated Requests
```

Protected endpoints require the JWT token through the `Authorization` header.

---

## 📦 Product API

Products are stored in MongoDB.

### Get Products

```http
GET /products/
```

Returns the available product catalog.

### Create Product

```http
POST /products/
```

Example:

```json
{
  "name": "Canvas Backpack",
  "description": "Durable everyday backpack",
  "price": 2499,
  "category": "Bags",
  "stock": 20,
  "image": "https://example.com/image.jpg"
}
```

### Update Product

```http
PUT /products/{product_id}
```

### Product Data

Products support:

* Name
* Description
* Price
* Category
* Stock
* Image URL

---

## 🛒 Cart & Order Flow

The application supports the complete shopping flow:

```text
Browse Products
      ↓
Add Product to Cart
      ↓
View Cart
      ↓
Checkout
      ↓
Place Order
      ↓
Order Created
```

The frontend communicates with the backend through REST APIs during each stage.

---

## 📚 API Documentation

FastAPI automatically provides interactive API documentation.

### Swagger UI

https://cart-system-ylj0.onrender.com/docs

### OpenAPI

https://cart-system-ylj0.onrender.com/openapi.json

Swagger can be used to:

* Explore API endpoints
* View request schemas
* Test endpoints
* Test authentication
* Inspect API responses

---

## ⚙️ Local Setup

### Clone Repository

```bash
git clone https://github.com/ratneshbuilds03/fastapi-project-cart03.git
cd fastapi-project-cart03
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

Windows:

```powershell
venv\Scripts\activate
```

Linux / macOS:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file and configure the required environment variables.

```env
DATABASE_URL=your_mysql_database_url

MONGODB_URL=your_mongodb_connection_string

MONGODB_DB=cart_db

SECRET_KEY=your_secret_key
```

### Environment Variable Description

| Variable       | Description               |
| -------------- | ------------------------- |
| `DATABASE_URL` | MySQL database connection |
| `MONGODB_URL`  | MongoDB connection string |
| `MONGODB_DB`   | MongoDB database name     |
| `SECRET_KEY`   | JWT signing secret        |

> Never commit `.env` files or database credentials to GitHub.

---

## ▶️ Run Locally

Start the FastAPI development server:

```bash
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

---

## 🐳 Docker

The backend is Dockerized for consistent deployment.

### Build Image

```bash
docker build -t cart-system .
```

### Run Container

```bash
docker run -p 8000:8000 cart-system
```

For local development, the project can also be used with Docker Compose when the required database services are configured.

---

## 🌐 Production Deployment

The backend is deployed using **Render**.

### Production API

https://cart-system-ylj0.onrender.com

### Health Check

```http
GET /health
```

The production deployment connects to:

* Aiven MySQL
* MongoDB Atlas

The application is containerized using Docker before deployment.

---

## 🔗 Frontend

Cartify's frontend is deployed separately using Vercel.

**Frontend:**
https://cartify-pi-nine.vercel.app/

**Frontend Repository:**
https://github.com/ratneshbuilds03/cartify-frontend-2s

The backend is configured with CORS to allow the production frontend to communicate with the API.

---

## 📁 Project Structure

```text
fastapi-project-cart03/
│
├── app/
│   ├── main.py
│   ├── models/
│   ├── routes/
│   ├── schemas/
│   ├── services/
│   └── database/
│
├── tests/
│
├── dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
└── README.md
```

---

## 🔄 Application Flow

```text
                ┌─────────────────────┐
                │   Cartify Frontend  │
                │       Vercel        │
                └──────────┬──────────┘
                           │
                           │ REST API
                           ▼
                ┌─────────────────────┐
                │    FastAPI Backend  │
                │       Render        │
                └──────────┬──────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
       ┌─────────────┐           ┌─────────────┐
       │    MySQL    │           │   MongoDB   │
       │    Aiven    │           │    Atlas    │
       └─────────────┘           └─────────────┘
```

---

## 🧪 Testing

The project includes backend tests for important application functionality.

Testing can be executed using:

```bash
pytest
```

The test suite covers areas such as:

* Authentication
* Products
* Cart functionality
* Orders
* API behavior

---

## 🔒 Security

Security-related implementation includes:

* JWT authentication
* Password hashing
* Protected endpoints
* Pydantic request validation
* CORS configuration
* Environment-based secrets
* Database credentials kept outside source code

Production credentials and secrets should never be committed to the repository.

---

## 🔮 Future Improvements

Potential future improvements include:

* Payment gateway integration
* Admin dashboard
* Product search and filtering
* Product reviews and ratings
* Order history interface
* Inventory management
* Improved user account management
* Email/order notifications

---

## 🔗 Repository

**GitHub:**
https://github.com/ratneshbuilds03/fastapi-project-cart03

---

## 📄 License

This project is created for educational, portfolio, and placement purposes.
