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

## Seed Data and Tours

The `seed_core` command populates 15 iconic New Zealand tours with 30 labeled local images, FAQs, and departures.

The 15 seeded tours:
1. Taupō Lake Cruise (Water, Taupō) - NZ$249.00
2. Tongariro Alpine Crossing (Hiking, Tongariro) - NZ$185.00
3. Milford Sound Cruise (Water, Milford Sound) - NZ$210.00
4. Waitomo Glowworm Caves (Adventure, Waitomo) - NZ$95.00
5. Rotorua Māori Cultural Evening (Culture, Rotorua) - NZ$160.00
6. Abel Tasman Kayaking (Water, Abel Tasman) - NZ$175.00
7. Matamata Film Set Tour (Culture, Matamata) - NZ$120.00
8. Kaikōura Whale Watch (Wildlife, Kaikōura) - NZ$165.00
9. Mount Cook & Hooker Valley Track (Hiking, Mount Cook) - NZ$195.00
10. Franz Josef Glacier Valley Walk (Adventure, Franz Josef) - NZ$145.00
11. Queenstown Shotover Jet & Canyon Adventure (Adventure, Queenstown) - NZ$179.00
12. Bay of Islands Dolphin Cruise & Hole in the Rock (Wildlife, Bay of Islands) - NZ$155.00
13. Coromandel Cathedral Cove Coastal Walk (Hiking, Coromandel) - NZ$135.00
14. Te Puia Geothermal Valley & Pōhutu Geyser (Culture, Rotorua) - NZ$110.00
15. Fiordland Wilderness Expedition (Adventure, Fiordland, Archived) - NZ$450.00

Local image folders:
- `media/seed/tours/`: 30 labeled landscape images (2 per tour).
- `media/seed/guides/`: 3 guide portrait photos (Hemi Walker, Sarah Jenkins, Rangi Bennett).

## How to Run Tests

Run this command in the project root to run all tests:
python manage.py test

You can also run tests for a single app:
python manage.py test apps.core
python manage.py test apps.accounts

## Postman Collection and API Testing

The project includes a ready to import Postman collection and environment covering all 45 API endpoints.

Files in the repository root:
- `kiwi_trails.postman_collection.json`: Complete collection containing all 45 API calls across 8 folders.
- `kiwi_trails.postman_environment.json`: Pre-configured environment variables for local testing.

### How to Import and Use Postman

1. Open Postman on your computer.
2. Click the Import button in the top left corner.
3. Select or drag and drop both `kiwi_trails.postman_collection.json` and `kiwi_trails.postman_environment.json`.
4. In the environment dropdown in the top right, select `Kiwi Trails Local Dev`.
5. Ensure your Django server is running (`python manage.py runserver`).
6. Run `POST /auth/login (Customer)` or `POST /auth/login (Admin)`. The post response script automatically saves the authentication token to your environment, allowing you to run all protected endpoints immediately.

### API Endpoint Groups (8 Folders)

1. `01 - Accounts & Authentication` (6 requests): Register, customer login, admin login, logout, get profile, and update profile.
2. `02 - Tours & Catalog (Public)` (4 requests): List tours with filtering and sorting, tour details, list categories, and guide details.
3. `03 - Tours & Catalog (Admin)` (12 requests): List all tours including archived, create tour, update tour, change tour status, upload tour image, delete image, create/update/delete FAQs, manage guides, and create category.
4. `04 - Departures & Calendar` (5 requests): Tour departures, monthly availability calendar, create departure, update departure capacity, and update departure status.
5. `05 - Reviews` (3 requests): Public tour reviews, submit customer review on completed booking, and admin review moderation.
6. `06 - Coupons` (4 requests): Validate discount coupon, list coupons, create coupon, and update coupon status.
7. `07 - Bookings (Customer)` (7 requests): Price quote preview, create booking, list my bookings, booking details, cancel booking, download PDF invoice, and download calendar invite.
8. `08 - Bookings & Operations (Admin)` (5 requests): List bookings with filters, change booking status, view departure attendance list, mark attendance, and view admin dashboard metrics.

## Folder Layout

The project follows a modular structure where each folder has one owner.

Root folder files:
manage.py: Django command line tool
requirements.txt: list of Python packages
pyproject.toml: Ruff linter configuration
.env.example: template for environment settings
.gitignore: files that Git should ignore
README.md: project documentation
kiwi_trails.postman_collection.json: Postman API collection
kiwi_trails.postman_environment.json: Postman environment settings

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

