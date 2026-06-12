
# 🛒 Azad Shop: Distributed E-Commerce API

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.x-092E20.svg?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-API-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791.svg?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg?logo=docker&logoColor=white)

## 📖 Overview
Azad Shop is a modern, highly scalable e-commerce backend platform designed to connect and integrate all branches of Islamic Azad University across Iran. Built with a focus on clean architecture, performance optimization, and reliable data management, this platform serves as a robust foundation for high-traffic digital retail operations.

## ✨ Key Features
* **Scalable Architecture:** Designed to handle multiple branches and high concurrent user traffic.
* **RESTful API Design:** Fully documented and standardized endpoints using Django REST Framework (DRF).
* **Advanced Database Modeling:** Optimized relational data structures utilizing PostgreSQL, mitigating N+1 query issues.
* **Authentication & Authorization:** Secure JWT-based user authentication and role-based access control.
* **Asynchronous Processing:** (Optional) Ready for Celery & Redis integration for background task management.

## 🛠️ Tech Stack
* **Core:** Python, Django
* **API:** Django REST Framework (DRF)
* **Database:** PostgreSQL (Primary), SQLite (Development)
* **Deployment:** Docker, Docker Compose

## 🚀 Quick Start (Local Development)
To get the project up and running on your local machine using Docker:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Abolfazlparadox/azadshop.git](https://github.com/Abolfazlparadox/azadshop.git)
   cd azadshop



2. **Environment Variables:**
Create a `.env` file in the root directory and configure your variables:
```env
SECRET_KEY=your_secret_key
DEBUG=True
DB_NAME=azadshop_db
DB_USER=postgres
DB_PASSWORD=postgres

```


3. **Build and Run with Docker:**
```bash
docker-compose up --build

```


4. **Apply Migrations:**
```bash
docker-compose exec web python manage.py migrate

```


5. **Create Superuser:**
```bash
docker-compose exec web python manage.py createsuperuser

```



The API will be available at `http://localhost:8000/`.

## 📂 Project Structure

Briefly explaining the core modules of the system:

* `/users`: Authentication, profile management, and role definitions.
* `/products`: Catalog management, inventory tracking, and categories.
* `/orders`: Checkout processing, order history, and status tracking.
* `/core`: Global configurations, custom exceptions, and base models.

## ✉️ Contact

**Abolfazl Mohammadshahi** Software Engineer

LinkedIn: [https://www.linkedin.com/in/abolfazl-mohammadshahi-12b87b324]

Email: [abolfazlmohammadshahi78@gmail.com]
