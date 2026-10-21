# Kiwi Trails: Member 2 Build Guide for Google Antigravity

This file is for **Member 2**. You open the project in **Google Antigravity** and tell its agent, one at a time: "Run Step 0", "Run Step 1", and so on. The agent follows this file, writes the code on disk, runs the checks, updates the progress tracker, **commits and pushes after every step**, then waits for you.

Repository: `git@github.com:monikaritgithub/kiwi_trails.git` (https://github.com/monikaritgithub/kiwi_trails)
Tracker and documentation site (GitHub Pages): https://monikaritgithub.github.io/kiwi_trails/

Files that must be in the `gemini/` folder of the workspace before you start:

1. `gemini/kiwi-trails-01-database-design.md`
2. `gemini/kiwi-trails-02-api-design.md`
3. `gemini/kiwi-trails-03-coding-rules-and-folders.md`
4. `gemini/kiwi-trails-04-success-criteria.md`
5. `gemini/kiwi-trails-05-member2-gemini-guide.md` (this file)
6. `gemini/starter/` (the tracker site and the Pages workflow that Step 0 copies into the project)

## 1. How to work with Antigravity

**Once, before Step 0 (you do this by hand):**

1. Install Python 3.12 or newer and Git. Check with `python --version` and `git --version`.
2. Make sure Git can reach GitHub over SSH. Run `ssh -T git@github.com`. It must greet `monikaritgithub`. If it does not, add your SSH key to GitHub first.
3. Optional but recommended: install the GitHub CLI and run `gh auth login`. With it the agent can enable GitHub Pages, protect `main`, create labels and issues, and open pull requests. Without it the agent gives you a short manual checklist instead.
4. In Antigravity, open the empty project folder as the workspace. Put the `gemini/` folder inside it. Allow the agent to run terminal commands.
5. Save the **agent rules** from section 2 as a workspace rule (or paste them as your first message).

**Then, for every step:**

1. Type: `Run Step 0` (then `Run Step 1`, `Run Step 2`, and so on).
2. The agent reads that step in this file, does the work, runs the checks, commits and pushes, and reports. Read the report.
3. If a check failed, use a fix prompt from section 10 or ask the agent to fix it. Do not move on with a failing check.
4. Steps 6 and later: merge the previous pull request first (a teammate reviews it), then type `Run Step N`.

## 2. Agent rules (save once, applies to every step)

```text
You are the build agent for Member 2 of "Kiwi Trails", a tour booking website
(Django, Django REST Framework, SQLite, plain HTML/CSS/JS frontend).

PROJECT FACTS
- The workspace root is the repository root.
- Remote: git@github.com:monikaritgithub/kiwi_trails.git, main branch: main.
- The contract is in gemini/: 01 database design, 02 API design, 03 coding rules and
  folders, 04 success criteria, 05 my step-by-step guide. Follow them exactly. If two
  files disagree, stop and tell me before writing code.
- When I say "Run Step N", open gemini/kiwi-trails-05-member2-gemini-guide.md, find the
  section "Step N", and do exactly what it says, then the finish protocol below.

HOW TO WORK
1. Write files directly to disk at the paths named. Always complete files, never partial.
2. Run the commands yourself. If one fails, find the cause and fix it (at most twice).
   If it still fails, stop and show me the error. Never skip a failing check.
3. Only touch the files the step names, plus my tracker file site/progress/member-2.json.
   Never edit frontend/, site/progress/member-1.json, site/progress/member-3.json, or
   anything in apps/bookings/ except models.py, migrations/ and the stub services.py.

CODE RULES (every Python file)
1. Start with ONE multi-line docstring in simple English (2 to 5 short lines) saying
   what the file does. Empty __init__.py files have nothing.
2. NO other comments: no # comments, no function or class docstrings, no commented-out
   code.
3. Beginner-readable code: short functions that do one thing, clear names, early
   "if ... raise" checks, no clever tricks, no decorators or metaclasses of our own.
4. Business rules go in services.py. Views are thin: read the request, call a service
   function, return the response. Views never build { success, data } or error JSON;
   raise the error classes from apps/core/exceptions.py.
5. Money is always Decimal, rounded to two places, half up. Never float. Dates use
   django.utils.timezone.now(), always UTC aware. No raw SQL. Use select_related and
   prefetch_related on lists.
6. Names: snake_case files, functions and fields; PascalCase classes; serializers
   <Model><Purpose>Serializer; views <Thing><Action>View with Admin first for admin
   calls; URL names <thing>-<action>; JSON field names, status words and addresses
   exactly as in the API and database files. Never invent new ones.
7. Imports in three groups (standard library, Django and packages, our apps) with full
   paths, for example: from apps.core.exceptions import CouponInvalid
8. Ruff, line length 100. No print(), no unused imports, no secrets, no absolute paths.

FINISH PROTOCOL (the end of every step)
a. Run: ruff check . and ruff format . and python manage.py check, and, once tests
   exist, python manage.py test. Fix anything that fails.
b. Update site/progress/member-2.json: first change tasks of earlier steps from "review"
   to "done" if their branch is already merged into origin/main; then set the tasks of
   this step to "review" (Step 0: "done"); set "updated" to today's date (date +%F).
   A call's task is the one whose title is that call, for example "POST /auth/login".
c. git status. Stage only the files of this step. Commit with the commit message named
   in the step (imperative, lower case, 50 characters or fewer).
d. git push -u origin <the branch named in the step>. Never force push.
e. If the step says "open a pull request", run gh pr create (title = the commit-style
   title in the step, body = what changed, which calls or tables, how it was tested).
   If gh is not available, print the link
   https://github.com/monikaritgithub/kiwi_trails/pull/new/<branch> for me.
f. Report in this order: files created or changed, check results, commit hashes, branch
   pushed, pull request link, tracker changes, anything I must do by hand. Then STOP and
   wait for my next instruction.

SAFETY
- Never push to main except in Step 0. Never commit .env, db.sqlite3, .venv or secrets.
- Never change a migration that is already on main. Never run destructive commands
  outside generated folders without asking me.
```

## 3. What Member 2 builds

| Area | Folder | Calls | Also |
| --- | --- | --- | --- |
| Project and base | `config/`, `apps/core/`, root files | 0 | Response wrapper, errors, paging, permissions, token check, test helpers |
| Accounts | `apps/accounts/` | 5 | `User` model |
| Tours and content | `apps/catalog/` | 16 | `Category`, `Guide`, `Tour`, `TourImage`, `TourFaq` |
| Departures | `apps/departures/` | 5 | `get_seats_taken`, `is_booking_open` |
| Coupons | `apps/coupons/` | 4 | `apply_coupon`, `mark_coupon_used` |
| Reviews | `apps/reviews/` | 3 | `Review` model |
| Seeds | `apps/seeds/` | 0 | `seed_core`, `seed_reviews`, `seed_all`, `constants.py` |
| Bookings models only | `apps/bookings/models.py`, `apps/bookings/migrations/` | 0 | `Booking` and `Attendance` models; stubs for Member 3's two helpers |

Total: **33 calls**. Member 3 builds the other 12 and Member 1 builds the frontend.

You also own the `gemini/` folder (the five team files). You never edit: the rest of `apps/bookings/`, or `frontend/`.

## 4. Branch, commit and push plan

Every step ends with a push. Branch names follow `<type>/<member>-<short-what>`.

| Step | Branch | Commit messages | Pull request |
| --- | --- | --- | --- |
| 0 | `main` (the only direct push) | `chore(core): create project structure`, `chore(docs): add team tracker and pages workflow` | no |
| 1 | `chore/m2-skeleton` | `chore(core): add project settings and root files` | no |
| 2 | `chore/m2-skeleton` | `feat(core): add response wrapper, errors, paging and token check` | no |
| 3 | `chore/m2-skeleton` | `db(accounts): add user model`, `db(catalog): add catalog models` | no |
| 4 | `chore/m2-skeleton` | four `db(...)` commits, one per app | no |
| 5 | `chore/m2-skeleton` | `chore(core): add helper stubs and empty seed commands` | yes, `chore(core): add project skeleton` |
| 6 | `feat/m2-accounts` | `feat(accounts): add register, login, logout and profile` | yes |
| 7 | `feat/m2-tours-public` | `feat(catalog): add public tour, category and guide calls` | yes |
| 8 | `feat/m2-tours-admin` | `feat(catalog): add admin tour calls` and similar | yes |
| 9 | `feat/m2-departures` | `feat(departures): add departure calls and seat rules` | yes |
| 10 | `feat/m2-coupons` | `feat(coupons): add coupon rules and calls` | yes |
| 11 | `feat/m2-reviews` | `feat(reviews): add review calls` | yes |
| 12 | `db/m2-seed-core` | `db(seeds): add core seed data` | yes |
| 13 | `docs/m2-readme` | `docs(docs): add project readme` | yes |

## 5. Step 0: create the project, GitHub setup, tracker and Pages

Type `Run Step 0`. The agent does everything below in this order and stops with a report. It detects the operating system and uses the Windows PowerShell form of a command when needed.

### 0.1 Check the tools

- `python --version` is 3.12 or newer, `git --version` works.
- `ssh -T git@github.com` greets `monikaritgithub`. If not, **stop** and tell me.
- Check that `gemini/` has the five `.md` files and the `starter/` folder. If not, stop.
- Check if `gh` is installed and logged in (`gh auth status`). Remember the answer for 0.9.

### 0.2 Git and the remote

```bash
git init -b main
git remote add origin git@github.com:monikaritgithub/kiwi_trails.git
git ls-remote --heads origin
```

If the remote already has branches, **stop** and ask me. If it is empty, continue.

### 0.3 Virtual environment and packages

```bash
python -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\Activate.ps1
pip install django djangorestframework django-cors-headers pillow reportlab python-dotenv ruff
pip freeze > requirements.txt
```

### 0.4 Django project and the eight apps

```bash
django-admin startproject config .
mkdir apps
touch apps/__init__.py                 # Windows: New-Item apps\__init__.py -ItemType File
for app in core accounts catalog departures coupons reviews bookings seeds; do
  mkdir apps/$app
  python manage.py startapp $app apps/$app
  rm apps/$app/tests.py
  mkdir apps/$app/tests
  touch apps/$app/tests/__init__.py
done
for app in accounts catalog departures coupons reviews bookings; do
  touch apps/$app/serializers.py apps/$app/services.py apps/$app/urls.py
done
rm -r apps/core/models.py apps/core/admin.py apps/core/views.py apps/core/migrations
rm -r apps/seeds/models.py apps/seeds/admin.py apps/seeds/views.py apps/seeds/migrations
mkdir -p apps/seeds/management/commands apps/bookings/management/commands
touch apps/seeds/management/__init__.py apps/seeds/management/commands/__init__.py
touch apps/bookings/management/__init__.py apps/bookings/management/commands/__init__.py
touch apps/core/authentication.py apps/core/exceptions.py apps/core/renderers.py
touch apps/core/pagination.py apps/core/permissions.py apps/core/testing.py
touch apps/seeds/constants.py
```

On Windows, do the same with PowerShell loops (`foreach`, `mkdir`, `Remove-Item`, `New-Item ... -ItemType File`).

### 0.5 Frontend and media folders

```bash
mkdir -p frontend/pages/admin frontend/css frontend/js/pages frontend/js/mock frontend/assets
mkdir -p media/seed media/tours
touch frontend/index.html
touch frontend/pages/admin/.gitkeep frontend/css/.gitkeep frontend/js/pages/.gitkeep
touch frontend/js/mock/.gitkeep frontend/assets/.gitkeep media/seed/.gitkeep media/tours/.gitkeep
```

### 0.6 `.gitignore`

Create `.gitignore` with exactly these lines:

```text
.venv/
__pycache__/
*.pyc
db.sqlite3
.env
media/tours/*
!media/tours/.gitkeep
site/docs/
.idea/
.vscode/
.ruff_cache/
```

### 0.7 First commit

Compare the folder layout with section 2.1 of the rules file. Then:

```bash
git add .
git reset gemini/starter
git commit -m "chore(core): create project structure"
```

The `gemini/` team files are part of this commit. `gemini/starter` is added in the next commit, together with the tracker.

### 0.8 Tracker site, Pages workflow and push to `main`

Copy the starter files into the project:

```bash
cp -r gemini/starter/site site
cp -r gemini/starter/.github .github
```

(On Windows use `Copy-Item -Recurse`.) Then:

1. Open `site/progress/member-2.json`, set the task `m2-step-0` to `done` and `updated` to today's date.
2. Check the site on this laptop: run `python -m http.server 8000` in the repository root and open `http://localhost:8000/site/`. The overview, the three member pages and the Documentation tab (it reads `gemini/`) must show. Stop the server afterwards.
3. Commit and push everything to `main`:

```bash
git add .
git commit -m "chore(docs): add team tracker and pages workflow"
git push -u origin main
```

### 0.9 GitHub settings

If `gh` works, the agent runs these. If not, it prints this list for me to do by hand on the GitHub website.

1. **Pages:** repository Settings, Pages, Source = **GitHub Actions**. With `gh`:

```bash
gh api -X POST repos/monikaritgithub/kiwi_trails/pages -f build_type=workflow
gh workflow run "Publish tracker and docs"
```

2. **Protect `main`:** Settings, Branches, a rule for `main` that requires a pull request and 1 approval before merging. With `gh`:

```bash
gh api -X PUT repos/monikaritgithub/kiwi_trails/branches/main/protection --input - <<'JSON'
{"required_status_checks": null, "enforce_admins": false,
 "required_pull_request_reviews": {"required_approving_review_count": 1},
 "restrictions": null}
JSON
```

3. **Invite** Member 1 and Member 3: Settings, Collaborators. (The agent cannot do this because it does not know their usernames.)
4. **Labels and issues:** create labels `member-1`, `member-2`, `member-3`, then one issue for each of the 45 calls in the quick index of `gemini/kiwi-trails-02-api-design.md`. The title is the call, for example `POST /bookings`, and the label is the "Built by" member.
5. **Board:** create a GitHub Project with the columns To do, Doing, Review, Done and add the issues (by hand).

Notes: GitHub Pages on a **private** repository needs a paid GitHub plan, and so does branch protection on a private repository. On a free account, make the repository public, or skip item 2 and keep the rule "nobody pushes to main" by agreement.

### 0.10 Check that Step 0 worked

- `python manage.py check` runs (errors about `core` or `accounts` not being found are normal until Step 1).
- `git log --oneline` shows the two commits and `git status` is clean.
- On GitHub, the **Actions** tab shows "Publish tracker and docs" green (it can take a minute), and https://monikaritgithub.github.io/kiwi_trails/ opens the tracker with the five documents under Documentation.
- The agent then runs `git switch -c chore/m2-skeleton` and `git push -u origin chore/m2-skeleton`, so Steps 1 to 5 can start from that branch, and reports.

## 6. Phase 0: Steps 1 to 5, the skeleton (one pull request)

Branch: `chore/m2-skeleton`, created at the end of Step 0 and used by Steps 1 to 5. Each step ends with a commit and a push of this branch.

### Step 1: settings, URLs and root files

Files: `config/settings.py`, `config/urls.py`, `.env.example`, `pyproject.toml`, and each `apps/<app>/apps.py`. After it, copy `.env.example` to `.env`.

```text
Step 1: project settings and root files.

Write these complete files:
- config/settings.py: reads SECRET_KEY, DEBUG and CORS_ALLOWED_ORIGINS from .env with
  python-dotenv. INSTALLED_APPS has django apps, rest_framework,
  rest_framework.authtoken, corsheaders and our eight apps as "apps.core",
  "apps.accounts", "apps.catalog", "apps.departures", "apps.coupons", "apps.reviews",
  "apps.bookings", "apps.seeds". AUTH_USER_MODEL = "accounts.User". USE_TZ = True,
  TIME_ZONE = "UTC". SQLite database at BASE_DIR / "db.sqlite3". MEDIA_URL = "/media/",
  MEDIA_ROOT = BASE_DIR / "media". DEFAULT_AUTO_FIELD = BigAutoField. CorsMiddleware
  placed correctly. REST_FRAMEWORK uses: ExpiringTokenAuthentication from
  apps.core.authentication, renderer apps.core.renderers.ApiRenderer, exception
  handler apps.core.exceptions.api_exception_handler, pagination class
  apps.core.pagination.ApiPagination, default permission IsAuthenticated.
- config/urls.py: includes each app's urls.py under "api/v1/" (accounts, catalog,
  departures, coupons, reviews, bookings). Django's own admin at "django-admin/".
  In DEBUG, serve MEDIA_URL from MEDIA_ROOT. No trailing slashes in our paths.
- .env.example with SECRET_KEY, DEBUG=True, CORS_ALLOWED_ORIGINS for
  http://127.0.0.1:5500 and http://localhost:5500.
- pyproject.toml with Ruff: line-length 100, import sorting on, target current Python.
- The apps.py of each app: name = "apps.<app>", default_auto_field set.
```

Check: `python manage.py check` (it will complain about missing core files until step 2).
Commit message: `chore(core): add project settings and root files`

### Step 2: the `core` app

Files: `apps/core/exceptions.py`, `renderers.py`, `pagination.py`, `permissions.py`, `authentication.py`, `testing.py`.

```text
Step 2: write apps/core. Use section 1 and the error table of the API file.

- exceptions.py: class ApiError(Exception) with class attributes code and status_code,
  and an __init__(message, fields=None). One subclass per error code with the right
  HTTP status: Unauthenticated, Forbidden, NotFound, ValidationFailed (VALIDATION_ERROR,
  422; named ValidationFailed because DRF already has ValidationError), EmailTaken,
  SeatsUnavailable, BookingClosed, CancellationNotAllowed, InvalidStatusChange,
  CapacityConflict, CouponInvalid (422), ReviewNotAllowed (403). Also the function
  api_exception_handler(exc, context) that turns ApiError, DRF ValidationError (put
  each field's first message into "fields"), NotAuthenticated, AuthenticationFailed,
  PermissionDenied, NotFound and Http404 into
  { "success": false, "error": { "code", "message", "fields" } }. "fields" is always
  present, {} when empty.
- renderers.py: ApiRenderer based on JSONRenderer. Wrap normal data as
  { "success": true, "data": ... }. If the data is already the error shape, leave it.
- pagination.py: ApiPagination reading page and page_size (default 10, max 50). Bad
  values raise ValidationFailed. Output data is
  { "items", "page", "page_size", "total" }.
- permissions.py: IsAdmin, IsCustomer, IsOwnerOrAdmin (object permission; owner means
  obj.user == request.user).
- authentication.py: ExpiringTokenAuthentication based on DRF TokenAuthentication,
  keyword "Bearer". A token older than 24 hours is refused with Unauthenticated. Also
  a small function make_token(user) that deletes the old token, creates a new one and
  returns (token, expires_at) with expires_at = created + 24 hours.
- testing.py: helpers make_admin(), make_customer(), make_client(user) that returns an
  APIClient logged in with a token. Demo password Password123!.

Also write apps/core/tests/test_response_format.py that checks one success answer and
one error answer have the right shape.
```

Check: `python manage.py check`
Commit message: `feat(core): add response wrapper, errors, paging and token check`

### Step 3: models, part 1 (accounts and catalog)

Files: `apps/accounts/models.py`, `apps/catalog/models.py`.

```text
Step 3: models for accounts and catalog. Follow sections 2 to 6 of the database file.

- accounts/models.py: UserRole (TextChoices), UserManager (create_user, create_superuser
  using email), User based on AbstractBaseUser and PermissionsMixin with the columns in
  the users table. USERNAME_FIELD = "email", REQUIRED_FIELDS = ["full_name"]. Save the
  email in lower case in save(). Add is_staff as a property that is True when role is
  admin. db_table = "users".
- catalog/models.py: TourStatus (TextChoices), Category, Guide, Tour, TourImage, TourFaq
  with every column, field type, default, index (location, status) and on_delete from the
  database file, and db_table for each (categories, guides, tours, tour_images,
  tour_faqs). Guide.languages is comma separated text.
```

Commit messages: `db(accounts): add user model` and `db(catalog): add catalog models` (two commits, each with its migration if one exists)

### Step 4: models, part 2 (departures, coupons, bookings, reviews)

Files: `apps/departures/models.py`, `apps/coupons/models.py`, `apps/bookings/models.py`, `apps/reviews/models.py`.

```text
Step 4: models for departures, coupons, bookings, attendance and reviews. Follow the
database file exactly, including TextChoices (DepartureStatus, CouponDiscountType,
BookingStatus, AttendanceStatus), indexes (departures.start_datetime, bookings.status),
unique fields, one-to-one links, on_delete rules, defaults and db_table names
(departures, coupons, bookings, attendance, reviews). Rating uses
PositiveSmallIntegerField with validators 1 to 5. Coupon.save() saves the code in
capitals. Do not put business rules in the models.
```

Then run:

```bash
python manage.py makemigrations accounts catalog departures coupons bookings reviews
python manage.py migrate
python manage.py makemigrations --check
```

Commit messages: `db(departures): add departure model`, `db(coupons): add coupon model`, `db(bookings): add booking and attendance models`, `db(reviews): add review model` (four commits, each with its migration).

### Step 5: helper stubs, empty URL files, empty seeds

Files: `services.py` in departures, coupons and bookings; `urls.py` in all six apps; `apps/seeds/constants.py` and the three seed commands.

```text
Step 5: stubs and empty files.

Write these as STUBS: right function name and inputs, fake but correctly shaped values.
Each stub file's top docstring must have a line starting with "STUB:" naming the stub
functions.
- apps/departures/services.py: get_seats_taken(departure) returns 0;
  is_booking_open(departure) returns True.
- apps/coupons/services.py: apply_coupon(code, subtotal) returns (None, Decimal("0.00"),
  subtotal); mark_coupon_used(coupon) does nothing.
- apps/bookings/services.py: complete_bookings_for_departure(departure) does nothing;
  get_completed_booking_for_user(booking_id, user) returns None.
Also write each app's urls.py with urlpatterns = [] (docstring only), and in
apps/seeds: constants.py (empty dictionaries for test departures and coupons for now),
management/__init__.py, management/commands/__init__.py, and seed_core.py, seed_reviews.py
and seed_all.py as commands whose handle() writes nothing yet. seed_all calls the other
three with call_command in this order: seed_core, seed_bookings, seed_reviews.
```

Check: `python manage.py check`, `ruff check .`, `ruff format .`, `python manage.py test`, `python manage.py runserver`
Commit message: `chore(core): add helper stubs and empty seed commands`

After the push, open the Phase 0 pull request (title `chore(core): add project skeleton`). Member 1 or Member 3 reviews it. Steps 6 and later start only after it is merged.

## 7. Phase 1: Steps 6 to 13, build the calls

Each step is one branch and one pull request. Start every step with `git switch main && git pull`, then create the step's branch. Follow the build order from the rules file. Each step ends with a commit, a push and a pull request (see the finish protocol in section 2). Start a step only after the previous pull request is merged.

Before writing code in each step, the agent reads the real models and `apps/core/exceptions.py` from the project, so it uses the real names.

### Step 6: accounts (5 calls)

Branch: `feat/m2-accounts`. Files: `apps/accounts/serializers.py`, `services.py`, `views.py`, `urls.py`, `tests/test_accounts.py`, `admin.py`.

```text
Step 6: accounts. Build the five calls in section 5.1 of the API file: POST /auth/register,
POST /auth/login, POST /auth/logout, GET /users/me, PUT /users/me.
- services.py: register_user, login_user, logout_user, update_profile. login_user uses
  make_token from apps.core.authentication. Same UNAUTHENTICATED message for a wrong email
  and a wrong password. EmailTaken has fields {"email": "Email is already used."}.
- serializers.py: RegisterSerializer, LoginSerializer, UserSerializer,
  UserUpdateSerializer with the rules in the field tables. The password is never returned.
- views.py: RegisterView, LoginView (both public), LogoutView, MeView (get and put).
- urls.py paths without a trailing slash; names like auth-register.
- tests/test_accounts.py: a success test and one test per listed error for each call.
Responses must match the examples in the API file exactly.
```

Check: `python manage.py test apps.accounts`
Commit message: `feat(accounts): add register, login, logout and profile`

### Step 7: tours, public side (4 calls)

Branch: `feat/m2-tours-public`. Files: `apps/catalog/serializers.py`, `services.py`, `views.py`, `urls.py`, `tests/test_tours_public.py`.

```text
Step 7: public catalog calls: GET /tours, GET /tours/{id}, GET /categories,
GET /guides/{id}. Follow section 5.2 of the API file and the TourSummary and TourDetail
shapes in section 3.
- services.py: list_tours(filters) with search, location, category_id, min_price,
  max_price and sort, only active tours. Work out average_rating, review_count,
  next_departure and seats_left in ONE annotated query with select_related. get_tour(id,
  user) hides archived tours from non-admins with NotFound.
- serializers.py: TourSummarySerializer, TourDetailSerializer, CategorySerializer,
  GuideSerializer (languages as a list), TourImageSerializer, TourFaqSerializer. Empty
  optional values are sent as null. Use get_seats_taken and is_booking_open from
  apps.departures.services for departure rows.
- views.py: TourListView, TourDetailView, CategoryListView, GuideDetailView.
- tests: success, a bad sort value, an archived tour, and an assertNumQueries test
  proving the tour list does not run one query per tour.
```

Check: `python manage.py test apps.catalog`
Commit message: `feat(catalog): add public tour, category and guide calls`

### Step 8: tours, admin side (12 calls)

Branch: `feat/m2-tours-admin`. Files: same folder, plus `tests/test_tours_admin.py`.

```text
Step 8: admin catalog calls from section 5.2: GET /admin/tours, POST /admin/tours,
PUT /admin/tours/{id}, PATCH /admin/tours/{id}/status, POST /admin/tours/{id}/images,
DELETE /admin/tour-images/{id}, POST /admin/tours/{id}/faqs, PUT and DELETE
/admin/faqs/{id}, POST /admin/guides, PUT /admin/guides/{id}, POST /admin/categories.
- Add TourWriteSerializer and write serializers for guides, FAQs, images and categories.
  The tour create answer is the full TourDetail shape.
- services.py: create_tour, update_tour, set_tour_status, add_tour_image (JPG, PNG or WebP
  up to 5 MB, saved under media/tours/, image_url like /media/tours/<file>),
  delete_tour_image, create_faq, update_faq, delete_faq, create_guide, update_guide,
  create_category.
- Views named Admin...View, all using the IsAdmin permission. Image upload is
  multipart/form-data.
- tests: success and every error listed for each call, including 401 and 403.
```

Check: `python manage.py test apps.catalog`
Commit messages: one commit per group of calls, for example `feat(catalog): add admin tour calls` and `feat(catalog): add admin guide and category calls`

### Step 9: departures (5 calls and 2 helpers)

Branch: `feat/m2-departures`. Files: `apps/departures/serializers.py`, `services.py` (replace the stub), `views.py`, `urls.py`, `tests/test_departures.py`.

```text
Step 9: departures. Replace the stubs and build section 5.3 of the API file.
- services.py: get_seats_taken(departure) sums traveller_count of pending, approved and
  completed bookings. is_booking_open(departure) follows the booking_open rule. Also
  get_seats_left, list_upcoming_departures(tour), list_calendar(month), create_departure,
  update_departure (CapacityConflict with the exact message and fields from the API
  file), change_departure_status. For "completed", call
  complete_bookings_for_departure from apps.bookings.services inside the same
  transaction.atomic(); import it inside that function to avoid a circular import.
- Remove the STUB: line from the file's docstring.
- serializers.py: DepartureSerializer, DepartureCalendarSerializer (adds tour_title),
  DepartureWriteSerializer (start in the future, deadline before start, capacity at
  least 1).
- Views: TourDepartureListView, DepartureCalendarView, AdminDepartureCreateView,
  AdminDepartureUpdateView, AdminDepartureStatusView.
- tests for every call and every error, plus tests for get_seats_taken and
  is_booking_open.
```

Check: `python manage.py test apps.departures`
Commit message: `feat(departures): add departure calls and seat rules`

### Step 10: coupons (4 calls and 2 helpers)

Branch: `feat/m2-coupons`. Files: `apps/coupons/serializers.py`, `services.py` (replace the stub), `views.py`, `urls.py`, `tests/test_coupons.py`.

```text
Step 10: coupons. Replace the stubs and build POST /coupons/validate, GET and POST
/admin/coupons, PUT /admin/coupons/{id} (section 5.4 of the API file).
- services.py: apply_coupon(code, subtotal) returns (coupon, discount_amount, new_total)
  and raises CouponInvalid with a clear message for unknown, switched off, expired and
  used-up codes. Not case sensitive. Percent discount rounds half up to two decimals.
  A fixed discount never takes the total below 0.00. mark_coupon_used(coupon) adds 1 to
  times_used with an F() update. Also create_coupon and update_coupon (the code cannot
  change).
- Remove the STUB: line from the docstring.
- serializers.py: CouponSerializer, CouponCreateSerializer (code 3 to 30 letters or
  digits, discount_value above 0 and at most 100 for percent, expiry in the future,
  max_uses at least 1), CouponUpdateSerializer, CouponValidateSerializer.
- Views: CouponValidateView, AdminCouponListCreateView, AdminCouponUpdateView.
- tests for every call, every error, and each of the four invalid-coupon cases.
```

Check: `python manage.py test apps.coupons`
Commit message: `feat(coupons): add coupon rules and calls`

### Step 11: reviews (3 calls)

Branch: `feat/m2-reviews`. Files: `apps/reviews/serializers.py`, `services.py`, `views.py`, `urls.py`, `tests/test_reviews.py`.

```text
Step 11: reviews. Build GET /tours/{id}/reviews, POST /reviews, GET /admin/reviews
(section 5.4 of the API file).
- services.py: list_tour_reviews(tour_id) newest first; create_review(user, booking_id,
  rating, comment) uses get_completed_booking_for_user from apps.bookings.services and
  raises ReviewNotAllowed (403) when the booking is not completed, not the caller's, or
  already reviewed; tour comes from the booking.
- serializers.py: ReviewSerializer (reviewer_name is first name and last initial, for
  example "Aroha S."), ReviewAdminSerializer (adds user_id and tour_title),
  ReviewCreateSerializer.
- Views: TourReviewListView, ReviewCreateView, AdminReviewListView with filters tour_id
  and rating.
- tests for success and each error. Because the real booking helper may still be a stub,
  create the test booking and patch get_completed_booking_for_user.
```

Check: `python manage.py test apps.reviews`
Commit message: `feat(reviews): add review calls`

### Step 12: seed commands

Branch: `db/m2-seed-core`. Files: `apps/seeds/constants.py`, `management/commands/seed_core.py`, `seed_reviews.py`, `seed_all.py`.

```text
Step 12: seed data. Follow section 7 of the database file exactly.
- constants.py: names of the test departures (full, closed, cancelled) and the five
  coupon codes, so Member 3 can find them.
- seed_core.py: 1 admin admin@kiwitrails.test and 5 customers (aroha@, tane@, mei@,
  liam@, sione@kiwitrails.test), 5 categories, 3 guides, 9 tours (1 archived, prices
  and durations mixed, macron names like Taupō kept), 2 images per tour with alt_text
  (paths under /media/seed/), 2 to 3 FAQs per tour, departures (3 per active tour: 1
  past completed and 2 future scheduled, plus a cancelled future one, a future one with
  capacity 4 called "full", and one whose booking_deadline already passed called
  "closed"), and the five coupons SUMMER10, WELCOME20, EXPIRED5, SWITCHEDOFF, ONEUSE
  (used once). All dates made from now. Password Password123!.
- seed_reviews.py: 3 reviews on 3 of the 4 completed bookings (ratings 5, 4 and 3, one
  with no comment). Leave the 4th unreviewed.
- seed_all.py: runs seed_core, seed_bookings, seed_reviews in order.
- Every command: safe to run twice (get_or_create or update_or_create), a --reset
  option that deletes only its own rows, and prints counts with self.stdout.write.
- seed_all must skip seed_bookings with a clear message if that command does not exist
  yet, until Member 3 merges it.
```

Check:

```bash
rm db.sqlite3 && python manage.py migrate
python manage.py seed_core
python manage.py seed_core
```

The second run must make no duplicates.
Commit message: `db(seeds): add core seed data`

### Step 13: finish and join up

Branches: `docs/m2-readme`, then small `fix/...` branches.

```text
Step 13: final README.md for the root. Sections: what the project is, setup steps, reset
steps (delete db.sqlite3, migrate, seed_all), seeded logins (admin and customers, the
password), how to run the tests, how to run the frontend, the folder layout from section
2 of the coding rules file, and the team rules in five lines. Simple English, no
comments or marketing words.
```

Phase 2 checks for Member 2:

- Search the whole project for `STUB:`; none may be left in your files.
- Run `python manage.py test`; it must pass.
- Run the reset steps and compare the counts with Member 1 and Member 3.
- Walk through the seeded cases: full departure, closed departure, archived tour, rejected booking, completed booking with and without a review.

After the freeze: `git tag v1.0`.

## 8. The progress tracker

The tracker page is https://monikaritgithub.github.io/kiwi_trails/. It has an overview, one page for each member, and all five team documents in a readable form with a table of contents. It updates by itself a minute or two after every merge into `main` that changes `site/` or `gemini/`.

How it works:

- `site/index.html` is the page. Member 2 owns it.
- `site/progress/member-1.json`, `member-2.json` and `member-3.json` hold each member's tasks. **Each member edits only their own file.**
- A task is `{ "id", "title", "status", "note" }` and `status` is `todo`, `doing`, `review` or `done`. "Percent" on the page means tasks marked `done`.
- The tracker file is changed in the **same pull request** as the work, so progress and code move together. No separate pull requests are needed.
- The workflow `.github/workflows/pages.yml` copies `gemini/*.md` into the site when it publishes, so the documents on the page are always the ones in the repository.

For Member 2, the agent updates `site/progress/member-2.json` in the finish protocol of every step. For Members 1 and 3, the rule is: when you open a pull request set its tasks to `review`; when it is merged, set them to `done` in your next pull request. A short `note` is welcome, for example "waiting for Member 2's login".

## 9. Checks before every pull request

```bash
git pull --rebase origin main
ruff check .
ruff format .
python manage.py makemigrations --check
python manage.py test
```

Then read the code once yourself:

- [ ] The first thing in every Python file is one short docstring, and there are no other comments
- [ ] No `print()`, no commented-out code, no unused imports
- [ ] Views are short and only call services
- [ ] No `float` anywhere near money
- [ ] Field names, addresses and status words match the API and database files
- [ ] I only changed files in Member 2's folders
- [ ] The pull request title follows `type(scope): summary` and the description says how I tested it

## 10. Fix prompts when the agent gets it wrong

```text
Remove every comment and every function or class docstring. Keep only the one multi-line
docstring at the top of each file. Rewrite those files on disk.
```

```text
This view contains business rules. Move them into services.py as plain functions and make
the view only read the request, call the service and return the result.
```

```text
You used float or a plain division for money. Use Decimal and round to two places, half up,
as in apps/coupons/services.py.
```

```text
The JSON does not match the API file. Compare your serializer with the example response in
section 5 of the API file, field by field, and fix the names, the null rules and the order.
```

```text
Make this simpler for a beginner. Shorter functions, clearer names, no nested comprehensions,
no tricks. The behaviour must not change.
```

```text
You changed or invented a field, address or status word. Use exactly the words in the
database and API files and tell me if something is missing instead of inventing it.
```

```text
The test <test name> fails. Read the error, find the smallest cause, fix it, and run the test again. Do not add comments.
```
