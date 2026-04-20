# 🍔 Burger Queen API

This repository contains the backend API for the Burger Queen Ordering System, built with Flask and Python.  
It provides endpoints to manage users, products, and orders, and integrates with JWT-based authentication to ensure secure access. 
The API was developed to be consumed by the [Burger Queen frontend app](https://github.com/florsalvador/burger-queen).

---

## 📋 Features

- JWT-based authentication and authorization
- User management (admins can create, update, and delete users)
- Product management (CRUD operations for menu items)
- Order management (create, update status, delete, and list orders)
- Role-based access control (Admin, Waiter, Chef)
- CORS enabled to allow frontend integration
- Health check endpoint for deployment monitoring

---

## 🖥️ Tech Stack

- **Framework:** Flask
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **Authentication:** Flask-JWT-Extended, Flask-Bcrypt
- **CORS:** Flask-CORS
- **Deployment:** Render (cloud hosting)

---

## 🚀 Deployment

The API is deployed on Render: 👉 [Live API](https://burger-queen-api-cqif.onrender.com)

⚠️ **Note:** The first request after a period of inactivity may fail. Simply retry and it will work.

### Test Credentials

| Role   | Email            | Password |
|--------|------------------|----------|
| Admin  | admin@email.com  | 123456   |
| Chef   | chef@email.com   | 123456   |
| Waiter | waiter@email.com | 123456   |

---

## 🔑 Environment Variables

Before running the app, create a `.env` file in the root directory with the following variables:

```bash
DATABASE_URL=your_postgresql_database_url
JWT_SECRET_KEY=your_secret_key
```

- DATABASE_URL: PostgreSQL connection string
- JWT_SECRET_KEY: Secret key for signing JWT tokens

---

## ⚙️ Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/your-username/burger-queen-api.git
cd burger-queen-api
pip install -r requirements.txt
```

Run the app locally:

```bash
flask --app api.app:app run
```

By default, the API will be available at:
http://127.0.0.1:5000

---

## 📚 API Endpoints

### Authentication

- `POST /login` → Login with email & password, returns JWT token

### Health Check

- `GET /health` → Returns { "status": "ok" }

### Users (Admin only)

- `GET /users` → List all users
- `POST /users` → Create a new user
- `PATCH /users/:id` → Update user
- `DELETE /users/:id` → Delete user

### Products

- `GET /products` → List all products
- `POST /products` → Create a new product
- `PATCH /products/:id` → Update product
- `DELETE /products/:id` → Delete product

### Orders

- `GET /orders` → List all orders
- `POST /orders` → Create a new order
- `PATCH /orders/:id` → Update order status
- `DELETE /orders/:id` → Delete an order

---

## 👥 Roles

- **Admin** → Manage users and products
- **Waiter** → Take customer orders and send them to the kitchen
- **Chef** → View incoming orders and mark them as ready

---

## 🧪 Testing

Use Postman or Insomnia to interact with the API.  
Make sure to include the JWT token in the Authorization header:

```bash
Authorization: Bearer <your_token>
```

