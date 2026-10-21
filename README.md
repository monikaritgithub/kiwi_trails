# Kiwi Trails

Kiwi Trails is a tour booking website for New Zealand travel.
The project uses Django and Django REST Framework for the backend API.
The frontend uses plain HTML, CSS, and JavaScript.
All data is stored in a SQLite database.

## Setup Steps

Follow these steps to set up the project on your computer.

1. Clone the repository and move into the folder:
git clone git@github.com:monikaritgithub/kiwi_trails.git
cd kiwi_trails

2. Create a virtual environment:
python -m venv .venv

3. Turn on the virtual environment:
On Windows:
.venv\Scripts\activate
On Linux or macOS:
source .venv/bin/activate

4. Install the required Python packages:
pip install -r requirements.txt

5. Create your local settings file:
On Windows:
copy .env.example .env
On Linux or macOS:
cp .env.example .env

6. Run the database migrations:
python manage.py migrate

7. Load the seed data:
python manage.py seed_all

8. Start the development server:
python manage.py runserver

The API is now running at http://127.0.0.1:8000/

## How to Run Frontend

Member 1 builds the frontend in the frontend folder.
To start the frontend, open a second terminal and run:

1. Move into the frontend folder:
cd frontend

2. Start a simple web server:
python -m http.server 5500

Open http://127.0.0.1:5500 in your browser to view the website.

## Reset Steps

When you want a clean database with fresh test data, run these commands:

1. Delete the SQLite database file:
On Windows:
Remove-Item db.sqlite3
On Linux or macOS:
rm db.sqlite3

2. Run the database migrations again:
python manage.py migrate

3. Seed the database again:
python manage.py seed_all

## Seeded Logins

All test accounts use the same password.

Password for all accounts:
Password123!

Admin account:
Email: admin@kiwitrails.test

Customer accounts:
1. Email: aroha@kiwitrails.test
2. Email: tane@kiwitrails.test
3. Email: mei@kiwitrails.test
4. Email: liam@kiwitrails.test
5. Email: sione@kiwitrails.test

## How to Run Tests

Run this command in the project root to run all tests:
python manage.py test

You can also run tests for a single app:
python manage.py test apps.core
python manage.py test apps.accounts

## Folder Layout

The project follows a modular structure where each folder has one owner.

Root folder files:
manage.py: Django command line tool
requirements.txt: list of Python packages
pyproject.toml: Ruff linter configuration
.env.example: template for environment settings
.gitignore: files that Git should ignore
README.md: project documentation

Core project folders:
gemini: project contracts and build guides
site: team progress tracker published to GitHub Pages
.github: GitHub Actions workflows
config: Django project settings and base URLs
apps: all backend apps
frontend: website HTML, CSS, and JavaScript
media: uploaded pictures and seed images

Apps inside the apps folder:
apps/core: shared error handlers, response format, and helpers
apps/accounts: user registration, login, and profiles
apps/catalog: tours, categories, guides, images, and questions
apps/departures: tour dates, seat counts, and calendars
apps/coupons: discount codes and validation
apps/reviews: customer ratings and reviews
apps/bookings: reservations and attendance
apps/seeds: commands to load demo data

## Team Rules

1. Never push code directly to the main branch.
2. Work only in your assigned app folders.
3. Keep views thin and put business logic into services.
4. Run tests and style checks before opening a pull request.
5. Every Python file starts with one short docstring and has no other comments.
