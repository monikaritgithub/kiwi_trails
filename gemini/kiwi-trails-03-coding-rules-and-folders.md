# Kiwi Trails: Coding Rules, Folder Structure and Parallel Workflow

The rules all three members follow so our code looks like one person wrote it and so we can build at the same time without breaking each other's work. Stack: **Django + Django REST Framework + SQLite**, with a plain HTML/CSS/JavaScript frontend.

Team tracker and documentation: https://monikaritgithub.github.io/kiwi_trails/

Companion files: `kiwi-trails-01-database-design.md` (tables), `kiwi-trails-02-api-design.md` (API calls), `kiwi-trails-04-success-criteria.md` (what "done" means per member) and `kiwi-trails-05-member2-gemini-guide.md` (Member 2's step-by-step build plan for Google Antigravity). Change a rule only after the team agrees.

## 1. Setup on every laptop

```bash
git clone git@github.com:monikaritgithub/kiwi_trails.git kiwi-trails && cd kiwi-trails
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
python manage.py migrate
python manage.py seed_all
python manage.py runserver         # API on http://127.0.0.1:8000
```

Frontend (Member 1), in a second terminal:

```bash
cd frontend
python -m http.server 5500         # site on http://127.0.0.1:5500
```

- The API allows the frontend address through `CORS_ALLOWED_ORIGINS` in `.env`.
- Everyone uses the same Python and Django version. Member 2 pins them in `requirements.txt`. If you add a package, add it to that file in your own pull request and tell the team.
- Settings that differ per laptop (`SECRET_KEY`, `DEBUG`, `CORS_ALLOWED_ORIGINS`) live in `.env`. `.env` is never committed; `.env.example` is.
- After every `git pull`, run `pip install -r requirements.txt` and `python manage.py migrate`.

## 2. Folder structure

This is the current standard Django layout: one **project folder** (`config/`) for settings, and one folder per **app** inside `apps/`. Member 2 creates all of it in Phase 0. After that, **every folder has exactly one owner and nobody else edits it.**

### 2.1 The tree

```text
kiwi-trails/
├── manage.py
├── requirements.txt
├── pyproject.toml                  Ruff settings
├── .env.example
├── .gitignore
├── README.md
├── gemini/                         the five team files (.md), the contract
│   └── starter/                    tracker site and Pages workflow, copied in Step 0
├── site/                           tracker and documentation site (GitHub Pages)
│   ├── index.html
│   └── progress/                   member-1.json, member-2.json, member-3.json
├── .github/
│   └── workflows/pages.yml         publishes the site
│
├── config/                         the Django project (settings only)
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/
│   ├── __init__.py
│   │
│   ├── core/                       shared base, built first, then frozen
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── authentication.py
│   │   ├── exceptions.py
│   │   ├── renderers.py
│   │   ├── pagination.py
│   │   ├── permissions.py
│   │   ├── testing.py
│   │   └── tests/
│   │
│   ├── accounts/                   users and login
│   ├── catalog/                    categories, guides, tours, images, FAQs
│   ├── departures/                 departures, seats, calendar
│   ├── coupons/                    coupons
│   ├── reviews/                    reviews
│   ├── bookings/                   bookings, attendance, dashboard
│   └── seeds/                      demo data commands
│
├── frontend/                       the website (Member 1)
│   ├── index.html
│   ├── pages/
│   │   └── admin/
│   ├── css/
│   ├── js/
│   │   ├── config.js
│   │   ├── api.js
│   │   ├── auth.js
│   │   ├── helpers.js
│   │   ├── pages/
│   │   └── mock/
│   └── assets/
│
└── media/
    ├── seed/                       sample pictures, committed (Member 1)
    └── tours/                      uploaded pictures, never committed (only .gitkeep)
```

### 2.2 Standard files inside every app

Every app in `apps/` (except `core` and `seeds`) has the same files, so everyone knows where to look:

```text
apps/<app>/
├── __init__.py
├── apps.py                 app name, for example name = "apps.catalog"
├── models.py               database tables and TextChoices lists only
├── serializers.py          checks incoming data and shapes outgoing data
├── views.py                thin views: read request, call a service, return response
├── urls.py                 the address list of this app
├── services.py             the business rules, written once
├── admin.py                registers models in Django's own admin site
├── migrations/             made by Member 2 only
└── tests/
    ├── __init__.py
    └── test_<area>.py
```

| File | What goes inside | What must never go inside |
| --- | --- | --- |
| `models.py` | Model classes, `TextChoices` lists, `class Meta: db_table` | Business rules, price maths, request handling |
| `serializers.py` | Input checks, output shapes (the JSON in the API file) | Database writes, business rules |
| `views.py` | One class per API call: read request, call one function in `services.py`, return the result | Business rules, hand-made `{ success }` JSON |
| `urls.py` | `path()` lines with `name=` | Anything else |
| `services.py` | Business rules: seats, prices, coupons, status changes. Each is a plain function | Request or response objects |
| `tests/` | Success and error tests for each call | Tests of other apps |

### 2.3 What goes inside each app and who owns it

| Folder | Owner | Contents |
| --- | --- | --- |
| `config/` | Member 2 | `settings.py` (apps, DRF, CORS, media, auth user, time zone), `urls.py` (includes each app's `urls.py` under `api/v1/`) |
| `apps/core/` | Member 2 | `exceptions.py` (`ApiError` and one class per error code, plus the error handler), `renderers.py` (the `{ success, data }` wrapper), `pagination.py` (`page`, `page_size`, max 50), `permissions.py` (`IsAdmin`, `IsCustomer`, `IsOwnerOrAdmin`), `authentication.py` (`ExpiringTokenAuthentication`, 24 hours), `testing.py` (test helpers) |
| `apps/accounts/` | Member 2 | Model `User` with its manager. Serializers for register, login, profile. Services `register_user`, `login_user`, `logout_user`, `update_profile`. Views `RegisterView`, `LoginView`, `LogoutView`, `MeView` |
| `apps/catalog/` | Member 2 | Models `Category`, `Guide`, `Tour`, `TourImage`, `TourFaq`. The tour list query with rating, next departure and seats in one annotated query. All tour, image, FAQ, guide and category calls (16) |
| `apps/departures/` | Member 2 | Model `Departure`. Services `get_seats_taken`, `is_booking_open`, calendar query, create, update, change status. The 5 departure calls |
| `apps/coupons/` | Member 2 | Model `Coupon`. Services `apply_coupon`, `mark_coupon_used`, create, update. Calls: validate and the three admin coupon calls |
| `apps/reviews/` | Member 2 | Model `Review`. Services to create a review and list a tour's reviews. The 3 review calls |
| `apps/seeds/` | Member 2 | `constants.py` (names of the test departures and coupons), management commands `seed_core`, `seed_reviews`, `seed_all` |
| `apps/bookings/` | **Member 3**, with two exceptions below | `serializers.py`, `views.py`, `urls.py`, `services.py` (quote, create, cancel, status change, attendance, dashboard, the two helpers Member 2 calls), `documents.py` (PDF invoice and `.ics` file), `admin.py`, `tests/`, `management/commands/seed_bookings.py`. The 12 booking calls |
| `apps/bookings/models.py` and `apps/bookings/migrations/` | **Member 2** | `Booking` and `Attendance` models. Member 3 asks Member 2 for any column change |
| `frontend/` | Member 1 | See 2.4 |
| `media/seed/` | Member 1 | Small sample pictures (JPG or WebP) and `guides/` photos |
| `site/index.html`, `.github/` | Member 2 | The tracker page and the workflow that publishes it to GitHub Pages |
| `site/progress/member-N.json` | Each member owns their own file | The task list and status (`todo`, `doing`, `review`, `done`) of that member |
| `gemini/` | Member 2 | The five team files that are given to Gemini. Anyone may open an issue to change them |
| Root files | Member 2 | `manage.py`, `requirements.txt`, `pyproject.toml`, `.env.example`, `.gitignore`. The final `README.md` is written by Member 2 in Phase 3 |

### 2.4 Frontend folder (Member 1)

| Path | What goes inside |
| --- | --- |
| `frontend/index.html` | Home page |
| `frontend/pages/*.html` | One file per customer screen: `login.html`, `register.html`, `profile.html`, `tour-list.html`, `tour-detail.html`, `departure-calendar.html`, `booking-form.html`, `my-bookings.html`, `booking-detail.html`, `review-form.html` |
| `frontend/pages/admin/*.html` | One file per admin screen: `dashboard.html`, `tours.html`, `tour-form.html`, `departures.html`, `bookings.html`, `attendance.html`, `coupons.html`, `reviews.html`, `guides.html`, `categories.html` |
| `frontend/css/` | `base.css` (colours, fonts), `layout.css`, `components.css` |
| `frontend/js/config.js` | The API address and the `USE_MOCK` switch |
| `frontend/js/api.js` | The only file that calls `fetch`. Adds the token, unwraps `{ success, data / error }` |
| `frontend/js/auth.js` | Saves, reads and clears the token; redirects to login |
| `frontend/js/helpers.js` | Show money (NZD) and dates (New Zealand time) |
| `frontend/js/pages/<page>.js` | The script for one page, same name as its html file |
| `frontend/js/mock/<area>.json` | Mock answers copied exactly from the API file |
| `frontend/assets/` | Logo and icons |

Member 1 may rename these files, but must tell the team first (see the decisions in section 9).

### 2.5 The ownership rules

1. **Work only in your own folders.** Read anything, edit only what you own.
2. Need a change in another member's folder? Open an issue or message the owner. Do not edit it yourself.
3. Only Member 2 edits `models.py`, `migrations/`, `config/` and `apps/core/`.
4. Apps talk to each other only through these functions:

| Function | Written by | Called by |
| --- | --- | --- |
| `apps.departures.services.get_seats_taken(departure)` | Member 2 | Member 3 |
| `apps.departures.services.is_booking_open(departure)` | Member 2 | Member 3 |
| `apps.coupons.services.apply_coupon(code, subtotal)` | Member 2 | Member 3 |
| `apps.coupons.services.mark_coupon_used(coupon)` | Member 2 | Member 3 |
| `apps.bookings.services.complete_bookings_for_departure(departure)` | Member 3 | Member 2 |
| `apps.bookings.services.get_completed_booking_for_user(booking_id, user)` | Member 3 | Member 2 |

   Everyone may also import from `apps.core` (errors, permissions, paging). Do not import any other function from another app's `services.py`. Models may be imported where a foreign key needs them.
5. Imports go at the top of a file. The one exception: when two `services.py` files would import each other, import inside the function that needs it. This happens when `departures.services` calls `complete_bookings_for_departure`.

## 3. Naming rules

### Files and folders

| What | Rule | Good | Bad |
| --- | --- | --- | --- |
| Python files and folders | lower `snake_case`, no spaces | `documents.py`, `seed_core.py` | `BookingServices.py`, `seed core.py` |
| Standard app files | use the standard names in 2.2 | `models.py`, `serializers.py`, `views.py`, `urls.py`, `services.py` | `my_views_final.py` |
| Test files | `test_<area>.py` inside `tests/` | `tests/test_booking_create.py` | `booking_test_2.py` |
| Management commands | `seed_<what>.py`, class `Command` | `seed_bookings.py` | `SeedBookings.py` |
| Images and other static files | lower `kebab-case` | `lake-cruise.jpg`, `hemi-walker.jpg` | `Lake Cruise (1).JPG` |
| Frontend files | lower `kebab-case` | `tour-list.html`, `booking-form.js` | `TourList.html` |

### Python names

| What | Rule | Example |
| --- | --- | --- |
| Model class | singular `PascalCase` noun | `Tour`, `TourImage`, `Booking` |
| Serializer class | `<Model><Purpose>Serializer` | `TourSummarySerializer`, `TourDetailSerializer`, `TourWriteSerializer` |
| View class | `<Thing><Action>View`, with `Admin` first for admin calls | `TourListView`, `BookingCancelView`, `AdminTourStatusView` |
| Permission class | `Is<Role>` | `IsAdmin`, `IsCustomer`, `IsOwnerOrAdmin` |
| Error class | the error code in `PascalCase`, based on `ApiError` | `SeatsUnavailable`, `CouponInvalid`, `BookingClosed` |
| Choice list | `<Model><Field>` using `TextChoices` | `BookingStatus.PENDING = "pending"` |
| Test class | `<Thing>Tests` | `BookingCreateTests` |
| Test method | `test_<what_should_happen>` | `test_create_booking_refuses_when_no_seats_left` |
| Function and variable | `snake_case`, a verb for functions | `get_seats_taken`, `apply_coupon`, `traveller_count` |
| Constant | `UPPER_SNAKE_CASE` | `MAX_PAGE_SIZE = 50` |
| Private helper | start with `_` | `_make_reference()` |

### Data and addresses

| What | Rule | Example |
| --- | --- | --- |
| Database table | plural `snake_case`, set with `db_table` | `tour_images` |
| Column and model field | `snake_case` | `price_per_person`, `booking_deadline` |
| JSON field names | `snake_case`, exactly as in the API file | `seats_left` |
| URL address | lower, plural nouns, hyphens, no verbs, **no trailing slash** | `/admin/tour-images/{id}` |
| URL name (`name=` in `path()`) | `<thing>-<action>` | `tour-list`, `booking-cancel` |
| Status words | lower case, exactly as in the database file | `pending`, `archived` |

### Git names

| What | Rule | Example |
| --- | --- | --- |
| Branch | `<type>/<member>-<short-what>`, lower `kebab-case` | `feat/m3-booking-create`, `fix/m2-coupon-rounding` |
| Pull request title | same format as a commit message | `feat(bookings): add quote endpoint` |

## 4. Code style

The code must be simple enough for a beginner to read.

### 4.1 Comments: one per file, at the top

- **Every Python file starts with one multi-line docstring** that says, in simple English, what the file does. Two to five short lines. Nothing else.
- **No other comments.** No `#` comments, no docstrings on classes or functions, no commented-out code. Good names make the code explain itself.
- Empty files such as `__init__.py` have no docstring.
- Frontend files follow the same idea: one comment block at the top of each `.js`, `.css` and `.html` file, and no others.
- A stub (a fake function used until the real one is merged) says so in the top docstring of its file, on a line that starts with `STUB:` and names the stub functions. Remove that line when the real code is merged.

Example of a file in our style:

```python
"""
Coupon rules.

Checks a coupon code and works out the discount.
Used by the quote and booking calls.
"""

from decimal import ROUND_HALF_UP, Decimal

from django.utils import timezone

from apps.core.exceptions import CouponInvalid
from apps.coupons.models import Coupon, CouponDiscountType

TWO_PLACES = Decimal("0.01")


def apply_coupon(code, subtotal):
    coupon = Coupon.objects.filter(code=code.upper()).first()
    if coupon is None:
        raise CouponInvalid("This coupon does not exist.")
    if not coupon.is_active:
        raise CouponInvalid("This coupon is switched off.")
    if coupon.expires_at <= timezone.now():
        raise CouponInvalid("This coupon has expired.")
    if coupon.max_uses is not None and coupon.times_used >= coupon.max_uses:
        raise CouponInvalid("This coupon has been used up.")

    if coupon.discount_type == CouponDiscountType.PERCENT:
        discount = subtotal * coupon.discount_value / 100
    else:
        discount = min(coupon.discount_value, subtotal)

    discount_amount = discount.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    return coupon, discount_amount, subtotal - discount_amount
```

### 4.2 Simple code

- Follow PEP 8. Use **Ruff** to check and format (`ruff check .` and `ruff format .`), line length 100, settings in `pyproject.toml`. Run both before every commit.
- Imports in three groups (standard library, Django and packages, our own apps), each sorted. Ruff does this. Always write full paths such as `from apps.core.exceptions import CouponInvalid`.
- Short functions that do one thing, ideally under 25 lines. Early `if ...: raise` checks instead of deep nesting.
- Clear names instead of clever tricks. No one-line tricks that a beginner cannot read. No metaclasses, no decorators of our own, no clever comprehensions with more than one `for`.
- **Thin views:** a view reads the request, calls a function in `services.py`, and returns the response. Business rules (seats, prices, status changes) live in `services.py`, written once, so the same rule is never copied.
- **One response format:** views never build the `{ success, data }` wrapper or error JSON by hand; they use `core` (renderer and exception handler). Raise an error class instead of returning an error by hand.
- **Money** is always `Decimal`, never `float`. Round to two decimals, half up.
- **Dates** are always timezone-aware UTC (`django.utils.timezone.now()`), never `datetime.now()`.
- **No raw SQL.** Use the Django ORM, and `select_related` / `prefetch_related` on lists so a list never makes one query per row.
- **Never trust the browser.** The server checks permissions, seats and prices every time.
- Write code in English. No `print()` in pull requests (seed commands write with `self.stdout.write`). Remove unused imports.
- Do not hard-code secrets, keys or absolute paths.

## 5. Git rules

### Commit message format

```
<type>(<scope>): <short summary>

<optional body: what changed and why>

<optional footer: Refs #12>
```

| Part | Rule |
| --- | --- |
| `type` | one of: `feat` new behaviour, `fix` bug fix, `refactor` no behaviour change, `test` tests only, `docs` documentation, `style` format only, `chore` setup or packages, `db` models, migrations or seed data |
| `scope` | the app or area: `accounts`, `catalog`, `departures`, `coupons`, `reviews`, `bookings`, `core`, `seeds`, `frontend`, `docs`, `deps` |
| `summary` | imperative ("add", not "added"), lower case, no full stop, 50 characters or fewer (72 is the hard limit) |
| body | optional; wrap at 72 characters; explain why |
| footer | `Refs #<issue>` or `Closes #<issue>`; breaking changes use `feat(scope)!:` and a `BREAKING:` line |

**Good**

```
feat(bookings): add quote endpoint
fix(coupons): round percent discount half up
db(departures): add booking_deadline column
test(bookings): cover overbooking of a full departure
chore(deps): pin reportlab version
feat(frontend): show seats left on tour card
```

**Bad**

```
update stuff
Fixed bug
feat: Added the booking and also the coupon and some tests
WIP
```

One logical change per commit. Commit small and often. A model change and its migration go in the same commit.

### Branches and pull requests

1. `main` is protected: nobody pushes to it directly, and it always runs (`migrate` and `python manage.py test` both pass).
2. Start every task from fresh `main`: `git switch main && git pull`, then `git switch -c feat/m3-booking-create`.
3. Keep a branch short, one task, one or two days at most. Push it at least once a day.
4. Before opening a pull request: `git pull --rebase origin main`, run `ruff check .`, `ruff format .`, `python manage.py test`.
5. The pull request title uses the commit format. The description says what changed, which calls or tables it touches, and how you tested it. Link the issue.
6. **Update your progress file** `site/progress/member-N.json` in the same pull request: set the tasks you built to `review`, and tasks from earlier merged pull requests to `done`.
7. **One other member reviews** and answers within one working day. Anything that touches `models.py`, migrations or `apps/core/` is also reviewed by Member 2. The reviewer also checks the folder rule in 2.5 and the comment rule in 4.1.
8. Merge with **squash and merge**, so `main` gets one clean commit per pull request. Then delete the branch.

### Never commit

`db.sqlite3`, `.env`, `.venv/`, `__pycache__/`, uploaded files in `media/tours/` (only `media/seed/` is committed), editor folders, any real password or key. All of these are in `.gitignore`.

## 6. Working in parallel

The idea: the design files are the **contract**. Because every table, every address, every field name and every error is already decided, each member can build their own part without waiting for the others, then everything plugs together.

### Phase 0: foundation (Member 2 leads, about one sitting)

Member 2 pushes one pull request that contains the skeleton, so everyone starts from the same base:

- Django project `config/`, all seven apps in `apps/` with the standard files from 2.2, `apps/core/` (response wrapper, error handler, paging, permissions, token login check), `requirements.txt`, `pyproject.toml`, `.env.example`, `.gitignore`, and the five team files in `gemini/`. The exact setup commands are in Step 0 of `kiwi-trails-05-member2-gemini-guide.md`.
- **Every model and its migrations** for all 11 tables, using the database file.
- Every app's `urls.py` already included in `config/urls.py`.
- The six helper functions from 2.5 as **stubs**: they have the right name and inputs and return fake but correctly shaped values. The top docstring of each stub file has a `STUB:` line.
- Empty seed commands and `apps/seeds/constants.py`.

While Member 2 does this: Member 3 writes test cases for the booking calls from the API file, and Member 1 sets up the frontend with the mock API. Nobody is blocked.

### Phase 1: build in parallel

| Member | Builds | Works against |
| --- | --- | --- |
| Member 1 | Screens and `frontend/js/api.js` | Mock JSON copied from the API file; switches each call to the real server when it is merged |
| Member 2 | Accounts, tours and content, departures, reviews, coupons; then `seed_core`, `seed_reviews`, `seed_all` | The database file and the API file |
| Member 3 | Bookings, cancel, invoice, calendar, admin bookings, attendance, dashboard; then `seed_bookings` | Stubs of Member 2's helpers until the real ones are merged |

Each API call in the API file becomes **one issue** (title: `POST /bookings`, assigned to its member). The board has four columns: To do, Doing, Review, Done. One call, one branch, one pull request.

Build order that unblocks others first:

1. **Member 2:** `register` and `login` first (everyone needs a token), then `GET /tours`, `GET /tours/{id}`, departures, `coupons.services`.
2. **Member 3:** `quote`, `create booking`, `my bookings`, then cancel and the admin calls, then invoice, calendar and dashboard.
3. **Member 1:** login, tour list and tour page first, then booking, then admin screens.

### Phase 2: join up

- Replace every stub and mock with the real thing. Search the code for `STUB:` and set `USE_MOCK` to `false`; no stub may be left.
- Everyone runs the reset steps (delete `db.sqlite3`, `migrate`, `seed_all`) and walks through the seeded test cases together: full departure, closed departure, archived tour, rejected booking, completed booking with and without a review.
- Fix bugs in small `fix(...)` pull requests. No new features during this phase.

### Phase 3: freeze

Only bug fixes and the final README. Tag the release (`git tag v1.0`).

### Daily routine

1. Morning: `git switch main && git pull`, `pip install -r requirements.txt`, `python manage.py migrate`.
2. Post three lines in the team chat: what I did, what I will do, what blocks me.
3. Work on your branch, commit small, push at least once a day.
4. Before you stop: push, and open a pull request if the task is finished.

### Avoiding conflicts

- Stay inside your own folders (section 2). Need a change somewhere else? Message the owner or open an issue; do not edit it yourself.
- Only Member 2 edits `models.py` and migrations, so migration numbers never clash. If two migrations ever clash, run `python manage.py makemigrations --merge` and commit the merge file.
- Never edit a migration that is already on `main`; add a new one.
- Changing a JSON field name, an address or a status word is a **team decision**: update the docs first, then everyone changes their code.
- Call other members' code only through the helper functions listed in 2.5. Do not import their private functions.
- Do not reformat files you do not own.
- Run `git pull --rebase origin main` often so conflicts are small. If you hit a conflict you do not understand, ask before you resolve it.

## 7. Testing

- Use Django's `TestCase` and DRF's `APITestCase`. Django builds a separate temporary database for tests, so tests never touch your `db.sqlite3`.
- `apps/core/testing.py` (Member 2) gives helpers to create an admin, a customer and a logged-in test client with a token.
- Every call has tests for the success case and for each error listed in the API file.
- Member 3 writes the overbooking test: two requests for the last seats, only one may succeed.
- `python manage.py test` must pass before every pull request.
- Test files follow the same comment rule as 4.1: one docstring at the top.

## 8. The few "never" rules

- Never push straight to `main`.
- Never commit a database, `.env`, or a password.
- Never edit someone else's folder without asking.
- Never change an applied migration.
- Never use `float` for money.
- Never rename a field, address or status word without the team agreeing.
- Never merge your own pull request without a review.
- Never add comments other than the one docstring at the top of a file.

## 9. Decisions to agree

These are assumptions. Tick each one once the team agrees, or comment with a change.

- [ ] Commit format `type(scope): summary` with the types and scopes in section 5.
- [ ] Branch names `<type>/<member>-<short-what>` and squash merge.
- [ ] Ruff for style (line length 100).
- [ ] Member 2 writes all models and migrations in Phase 0.
- [ ] Folder layout and ownership in section 2 (apps inside `apps/`, project in `config/`).
- [ ] Helper function names in 2.5.
- [ ] Frontend folder and file names in 2.4 (Member 1 confirms or replaces them).
- [ ] One docstring at the top of each file and no other comments.
- [ ] Issue board with the four columns and one issue per API call.
- [ ] The progress tracker on GitHub Pages: each member edits only their own `site/progress/member-N.json`, in the same pull request as the work.
