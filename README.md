# Kiwi Trails (Ara Aotearoa)

> A culturally responsive eco-tourism reservation and authentic guided tour platform for Aotearoa New Zealand. Built with Django, Django REST Framework, SQLite, and vanilla HTML5, CSS3, and ES6 JavaScript.

---

## 🚀 Quick Start (Single Click)

You can run the entire Kiwi Trails application with a **single click**!

### Windows
Double-click **`run.bat`** in the project root folder.

The launcher automatically:
1. Creates a Python virtual environment (`.venv`) if not present.
2. Installs and upgrades all required dependencies from `requirements.txt`.
3. Creates your local configuration file (`.env`) from `.env.example`.
4. Runs database migrations and seeds realistic sample data (tours, departures, guides, bookings, and coupons).
5. Launches the Django REST API backend (`http://127.0.0.1:8000/`).
6. Launches the Frontend server (`http://127.0.0.1:5500/frontend/`).
7. Automatically opens your default web browser to the application!

### macOS & Linux
Run the single-command launcher script:
```bash
chmod +x run.sh && ./run.sh
```

---

## 🔑 Seeded Login Accounts

All pre-seeded test accounts use the same password.

**Password for all accounts:** `Password123!`

| Role | Email | Capabilities |
| :--- | :--- | :--- |
| **Administrator** | `admin@kiwitrails.test` | Manage tours, departures, attendance rosters, coupons, review moderation, and operations dashboard |
| **Customer** | `aroha@kiwitrails.test` | Discover tours, use the matching quiz, book departures, redeem coupons, download PDF invoices & ICS calendar files, submit reviews |
| **Customer** | `tane@kiwitrails.test` | Verified traveler account with booking history |
| **Customer** | `mei@kiwitrails.test` | Verified traveler account |
| **Customer** | `liam@kiwitrails.test` | Verified traveler account |
| **Customer** | `sione@kiwitrails.test` | Verified traveler account |

---

## ⚙️ Manual Setup (Optional)

If you prefer to configure and run the servers manually in separate terminal windows:

### 1. Backend Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment configuration
copy .env.example .env    # On Windows
cp .env.example .env      # On macOS/Linux

# Apply migrations and seed sample database
python manage.py migrate
python manage.py seed_all

# Start Django development server
python manage.py runserver 127.0.0.1:8000
```
Backend API will be running at `http://127.0.0.1:8000/api/v1/` and Django admin at `http://127.0.0.1:8000/django-admin/`.

### 2. Frontend Setup
In a second terminal:
```bash
python serve_frontend.py
```
Open `http://127.0.0.1:5500/frontend/` in your browser.

---

## 🧭 Key Application Features

- **Personalized Tour Matching Quiz (`apps/matching`)**: Interactive quiz matching travelers to eco-tours based on interest, budget, duration, accessibility accommodations, and Māori-led operator preferences.
- **Tour Catalog & Discovery**: 15 curated New Zealand tours across Water, Hiking, Wildlife, Culture, and Adventure categories with high-resolution imagery and certified Kaitiaki guides.
- **Atomic Booking Engine**: Prevents overbooking with atomic seat-locking during reservation transactions.
- **Promotional Coupons**: Percentage and fixed-dollar discount code validation.
- **Automated Invoices & Calendar Sync**: Dynamic ReportLab PDF invoice generation and downloadable RFC 5545 `.ics` calendar invites.
- **Verified Customer Reviews**: Post-tour rating and moderation system.
- **Administrator Dashboard**: Operations roster with real-time departure attendance tracking, metrics, and catalog management.

---

## 🧪 Running Automated Tests

Run the full automated test suite (365 passing unit and integration tests):
```bash
python manage.py test
```

Run tests for a specific domain module:
```bash
python manage.py test apps.matching
python manage.py test apps.catalog
python manage.py test apps.bookings
python manage.py test apps.accounts
```

Code quality and linting verification:
```bash
ruff check .
```

---

## 📮 Postman API Collection

The repository includes a ready-to-import Postman collection and environment covering all 45+ API endpoints:
- `kiwi_trails.postman_collection.json`
- `kiwi_trails.postman_environment.json`

### Import Instructions:
1. Open Postman.
2. Click **Import** in the upper left.
3. Select both `kiwi_trails.postman_collection.json` and `kiwi_trails.postman_environment.json`.
4. In the top-right environment selector, choose **Kiwi Trails Local Dev**.
5. Run `POST /auth/login (Admin)` or `POST /auth/login (Customer)`. The test runner automatically sets the bearer token for subsequent authenticated requests.

---

## 📁 Project Architecture

```
kiwi_trails/
├── manage.py                          # Django management script
├── requirements.txt                   # Production and testing dependencies
├── pyproject.toml                     # Ruff linter configuration
├── run.bat                            # Windows single-click launcher
├── run.ps1                            # PowerShell launcher
├── run.sh                             # macOS/Linux launcher
├── serve_frontend.py                  # Static frontend server (port 5500)
├── start_backend.bat                  # Dedicated backend launcher
├── start_frontend.bat                 # Dedicated frontend launcher
├── kiwi_trails.postman_collection.json# Postman API test suite
├── kiwi_trails.postman_environment.json
├── config/                            # Project settings, WSGI/ASGI, root URLs
├── apps/
│   ├── accounts/                      # Authentication, registration, user profiles
│   ├── bookings/                      # Reservations, PDF invoices, attendance lists
│   ├── catalog/                       # Tours, categories, guides, FAQs, images
│   ├── core/                          # Standardized responses, error handling, permissions
│   ├── coupons/                       # Discount codes and validation engine
│   ├── departures/                    # Tour departure schedules and seat availability
│   ├── matching/                      # Tour matching quiz & recommendation engine
│   ├── reviews/                       # Verified customer ratings & reviews
│   └── seeds/                         # Database seeding commands and demo datasets
├── frontend/                          # Client-side web application
│   ├── index.html                     # Landing page and tour showcase
│   ├── css/                           # Modular CSS styling and custom properties
│   ├── js/                            # ES6 modules, API client, and page controllers
│   └── pages/                         # Customer and administrator views
├── media/                             # Labeled seed assets and user uploads
└── docs/                              # Technical project documentation
```

---

## 🌿 Te Tiriti o Waitangi Alignment

Kiwi Trails integrates the three principles of Te Tiriti o Waitangi into its software design:
- **Partnership (Pātuitanga)**: Direct representation of certified Māori-led tourism operators and Kaitiaki guides.
- **Participation (Whai Wāhitanga)**: Transparent pricing, open accessibility details, and verified traveler feedback.
- **Protection (Tiakitanga)**: Environmental guardianship via strict departure capacity limits to safeguard fragile natural ecosystems, alongside ethical data handling.
