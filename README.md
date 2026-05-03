# Restaurant Web Application

A robust web application for restaurant management built with **Django**, **PostgreSQL**, and **Docker**. This project is designed for easy collaboration and scalable deployment.

## 🚀 Features
- **Menu Management**: Categorized dishes with image support.
- **Table Booking**: Integrated reservation system.
- **Dockerized Architecture**: Consistent environment for all developers.
- **PostgreSQL**: Production-ready database setup.

## 🛠 Prerequisites
Before you begin, ensure you have the following installed:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## 📥 Getting Started

### 1. Clone the repository
```bash
git clone [https://github.com/Primary17/restaurant-webapp.git](https://github.com/Primary17/restaurant-webapp.git)
cd restaurant-webapp
```
### 2. Set up Environment Variables
Copy the example environment file and adjust values if necessary:
```bash
cp .env.example .env
```
### 3. Build and Run with Docker
Start the containers in detached mode:
```bash
sudo docker compose up --build -d
```
The application will be available at: http://localhost:8000

## ⚙️ Development Commands

### Database Migrations
If you've added new models or fields, generate and apply migrations:
```bash
# Generate migration files
sudo docker exec -it restaurant_web python manage.py makemigrations

# Apply migrations to the database
sudo docker exec -it restaurant_web python manage.py migrate
```
### Create a Superuser
To access the Django Admin panel (http://localhost:8000/admin), create an admin account:
```bash
sudo docker exec -it restaurant_web python manage.py createsuperuser
```
### Static Files
To collect static files (CSS, JS, Images) for production:
```bash
sudo docker exec -it restaurant_web python manage.py collectstatic --noinput
```

## 📂 Project Structure
* `/app` - Django project root.
* `/app/core` - Main application logic (Models, Views, Templates).
* `docker-compose.yml` - Docker services configuration.
* `Dockerfile` - Python environment configuration.
* `.env` - Local environment variables (do not commit!).

## 🤝 Contributing
1. Create a new branch: `git checkout -b feature/your-feature-name`.
2. Commit your changes: `git commit -m 'Add some feature'`.
3. Push to the branch: `git push origin feature/your-feature-name`.
4. Open a Pull Request.