# LucidGPT Backend

## Overview
The LucidGPT Backend is a RESTful API built with FastAPI to manage customers, vehicles, and service appointments. It is designed with modular architecture and supports scalability, maintainability, and testing.

## Features
- CRUD operations for customers, vehicles, and appointments.
- Database integration with SQLAlchemy and PostgreSQL.
- Fully tested with pytest for reliability.
- OpenAPI documentation available at `/docs`.

## Tech Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL (production), SQLite (development/testing)
- **ORM**: SQLAlchemy
- **Testing**: pytest

## Requirements
- Python 3.12+
- PostgreSQL (for production)

## Setup Instructions
### 1. Clone the Repository
```bash
git clone https://github.com/your-backend-repo/lucidgpt-backend.git
cd lucidgpt-backend
