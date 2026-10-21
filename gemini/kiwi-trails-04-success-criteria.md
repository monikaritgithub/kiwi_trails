# Kiwi Trails: Success Criteria by Team Member

This file says exactly when each member's work counts as **done**. Every line is a yes or no check. Tick it only when you have tested it yourself. A reviewer re-checks the ticked lines in the pull request.

Companion files: `kiwi-trails-01-database-design.md`, `kiwi-trails-02-api-design.md`, `kiwi-trails-03-coding-rules-and-folders.md`, `kiwi-trails-05-member2-gemini-guide.md`.

## 1. Shared criteria (every member, every pull request)

### 1.1 Code quality

- [ ] `ruff check .` and `ruff format .` report nothing to fix (Python)
- [ ] `python manage.py test` passes
- [ ] Every Python file starts with one multi-line docstring in simple English that says what the file does
- [ ] There are no other comments, no docstrings on classes or functions, and no commented-out code
- [ ] No `print()`, no unused imports, no hard-coded secrets or absolute paths
- [ ] Names follow section 3 of the rules file (files, classes, functions, URLs, branches)
- [ ] Functions are short and do one thing; a beginner can read them

### 1.2 Working rules

- [ ] Only files in your own folders were changed (the folder table in section 2.3 of the rules file)
- [ ] Other apps are used only through the six helper functions in section 2.5 of the rules file
- [ ] No JSON field name, address or status word was changed without a team decision and an update to the docs
- [ ] Money uses `Decimal`; dates use timezone-aware UTC
- [ ] The commit messages follow `type(scope): summary`
- [ ] My own file `site/progress/member-N.json` is updated in this pull request (tasks built are `review`, earlier merged tasks are `done`, `updated` is today's date)
- [ ] One other member reviewed the pull request; it was squash merged; the branch was deleted

### 1.3 A pull request is done when

- [ ] The description says what changed, which calls or tables it touches, and how it was tested
- [ ] The issue is linked and moved to Done
- [ ] `main` still runs after the merge: `migrate` and `python manage.py test` both pass

## 2. Member 1: Frontend

**Owns:** `frontend/` and `media/seed/`. Builds every screen that calls the API (45 calls in total) and supplies the sample pictures.

### 2.1 Setup and structure

- [ ] The site opens with `python -m http.server 5500` inside `frontend/`, with no build step
- [ ] Files and folders match section 2.4 of the rules file, all in lower `kebab-case`
- [ ] `config.js` holds the API address and a single `USE_MOCK` switch
- [ ] Every `.html`, `.js` and `.css` file starts with one short comment that says what it does, and has no other comments

### 2.2 The request file (`api.js`)

- [ ] It is the only file that calls `fetch`; no screen calls `fetch` directly
- [ ] It adds `Authorization: Bearer <token>` to every protected call
- [ ] It turns `{ success: true, data }` into the data, and `{ success: false, error }` into an error object with `code`, `message` and `fields`
- [ ] The image upload call sends `multipart/form-data` and does not set `Content-Type` by hand
- [ ] The invoice and calendar calls download a file instead of reading JSON
- [ ] With `USE_MOCK` on, every call returns JSON copied from the API file, with the same names and the same `null` for empty values
- [ ] Switching one call from mock to real changes nothing in the screens

### 2.3 Customer screens

Each screen has a loading state, an empty state and an error state, and works on a phone-width window.

- [ ] **Register:** all four fields; shows `EMAIL_TAKEN` and field errors next to the right input
- [ ] **Login:** saves the token; a wrong password shows the server message; logout clears the token
- [ ] **Profile:** shows and edits name and phone; password change sends both `current_password` and `new_password`
- [ ] **Tour list:** search, location, category, price range and sort; paging; each card shows image, price, rating (or "No reviews yet"), next departure and seats left
- [ ] **Tour page:** images, description, itinerary, accessibility information, visitor guidelines, meeting point, guide, FAQs, reviews with paging, and upcoming departures
- [ ] **Departure calendar:** month picker; full, closed and cancelled-looking cases are clear
- [ ] **Booking form:** shows a price quote from `POST /bookings/quote` whenever the traveller count or coupon changes; shows coupon errors; the book button follows `booking_open` and `seats_left`
- [ ] **My bookings and booking page:** status filter, reference, price breakdown, cancel button shown only when `can_cancel` is true, invoice download, calendar download
- [ ] **Review form:** only offered for completed bookings; rating 1 to 5 and optional comment; handles `REVIEW_NOT_ALLOWED`

### 2.4 Admin screens

- [ ] Admin screens are hidden from customers and redirect to login when the token is missing or expired
- [ ] **Dashboard:** the four numbers from `GET /admin/dashboard`, with all five booking statuses
- [ ] **Tours:** list including archived, create, edit, archive and restore
- [ ] **Images, FAQs, guides, categories:** add, edit and delete as the API allows
- [ ] **Departures:** create, edit capacity and dates, mark completed or cancelled; shows `CAPACITY_CONFLICT`
- [ ] **Bookings:** filters, search by reference or name, approve, reject, cancel and complete with an optional reason
- [ ] **Attendance:** list for one departure, mark present or absent
- [ ] **Coupons and reviews:** list with paging, create and switch off a coupon, filter reviews

### 2.5 Behaviour rules

- [ ] `UNAUTHENTICATED` sends the person to the login screen
- [ ] `error.message` is shown to the person and `error.fields` highlight the inputs
- [ ] Seats, prices, cancel rights and booking-open state are never worked out in the browser; the screens use `seats_left`, `booking_open`, `can_cancel` and `total_price` from the server
- [ ] Dates are shown in New Zealand time; money is shown as NZD with two decimals
- [ ] Every image has `alt` text; every input has a label; buttons can be used with the keyboard
- [ ] No inline secrets, no `console.log` left in the code

### 2.6 Sample pictures

- [ ] 2 or 3 small JPG or WebP pictures for each of the 9 tours, plus the guide photos, in `media/seed/`
- [ ] File names are lower `kebab-case` and match the paths used by `seed_core`
- [ ] Each picture is small (about 300 KB or less)

### 2.7 Member 1 final check

- [ ] `site/progress/member-1.json` shows every task `done`
- [ ] Every one of the 45 calls is used by a screen or is documented as not needed
- [ ] `USE_MOCK` is `false` and no mock is used anywhere
- [ ] After a fresh `seed_all`, the screens show these cases correctly: full departure, closed departure, archived tour, rejected booking, completed booking with a review, completed booking without a review, an empty list

## 3. Member 2: Foundation, accounts, catalog, departures, coupons, reviews and seeds

**Owns:** `config/`, `apps/core/`, `apps/accounts/`, `apps/catalog/`, `apps/departures/`, `apps/coupons/`, `apps/reviews/`, `apps/seeds/`, all migrations, `bookings/models.py`, the root files and `gemini/`. Builds 33 of the 45 calls.

### 3.1 Phase 0: the skeleton (one pull request)

- [ ] Step 0 of the Member 2 guide was completed: the project is pushed to `git@github.com:monikaritgithub/kiwi_trails.git`, `main` is protected, Member 1 and Member 3 are invited, and the issue board has the four columns
- [ ] The tracker and documentation site is live at https://monikaritgithub.github.io/kiwi_trails/ with the overview, three member pages and the five documents, and the Actions run "Publish tracker and docs" is green
- [ ] Each of Steps 1 to 13 ended with a commit and a push, and `site/progress/member-2.json` matches the real state of the work
- [ ] A new laptop can follow the setup in section 1 of the rules file and reach a running server
- [ ] The folder tree matches section 2.1 of the rules file; every app has the standard files from 2.2
- [ ] `requirements.txt` has pinned versions (Django, DRF, django-cors-headers, Pillow, ReportLab, python-dotenv, Ruff)
- [ ] `.env.example` and `.gitignore` are complete; `db.sqlite3`, `.env`, `.venv/`, `media/tours/` are ignored
- [ ] `pyproject.toml` sets Ruff to line length 100 with import sorting
- [ ] `AUTH_USER_MODEL = "accounts.User"` is set before the first migration; `USE_TZ = True`, `TIME_ZONE = "UTC"`
- [ ] All 11 tables exist with the exact names, columns, field types, choices, defaults, indexes and delete rules of the database file
- [ ] Every model sets `db_table`; every choice list is a `TextChoices` with the words from section 6 of the database file
- [ ] `python manage.py migrate` runs from an empty database with no error, and `makemigrations --check` finds nothing new
- [ ] Every app's `urls.py` is included in `config/urls.py` under `api/v1/`, with no trailing slashes
- [ ] The six helper functions exist as stubs with the right names and inputs, each stub file has a `STUB:` line in its top docstring
- [ ] The five team files and `gemini/starter/` are in `gemini/` and committed
- [ ] Member 1 and Member 3 can start their work from this pull request without asking anything

### 3.2 `apps/core` (built first, then frozen)

- [ ] Every success answer is `{ "success": true, "data": ... }` through the renderer, with no view building it by hand
- [ ] Every error answer is `{ "success": false, "error": { "code", "message", "fields" } }` and includes `fields` even when empty
- [ ] There is one error class for each code in the API file (12 codes), with the correct HTTP status; errors raised by DRF itself (404, 401, 403, validation) are changed to the right code
- [ ] A wrong `{id}` that is not an integer gives `NOT_FOUND`
- [ ] Paging reads `page` and `page_size` (default 10, max 50) and gives `VALIDATION_ERROR` for a bad value; the list answer has `items`, `page`, `page_size`, `total`
- [ ] The token check refuses a token older than 24 hours with `UNAUTHENTICATED`; the header is `Authorization: Bearer <token>`
- [ ] `IsAdmin`, `IsCustomer`, `IsOwnerOrAdmin` work, and the order of checks is 401, 403, 404, 422, 409
- [ ] `testing.py` can create an admin, a customer, and a client logged in with a token
- [ ] Core has its own tests

### 3.3 Accounts (5 calls)

- [ ] Register, login, logout, get profile and update profile return exactly the shapes in the API file
- [ ] The email is saved in lower case and must be unique; `EMAIL_TAKEN` has the `fields.email` message
- [ ] The password is stored as a hash and is never returned
- [ ] Login deletes the old token, makes a new one, and sends `token`, `expires_at` (created plus 24 hours) and `user`
- [ ] A wrong email and a wrong password give the same `UNAUTHENTICATED` message
- [ ] Logout deletes the token
- [ ] Profile update changes only the fields sent; `phone: null` clears it; a wrong `current_password` is a `VALIDATION_ERROR`

### 3.4 Catalog (16 calls)

- [ ] The public tour list shows only `active` tours; filters `search`, `location`, `category_id`, `min_price`, `max_price` and `sort` all work; a bad `sort` is `VALIDATION_ERROR`
- [ ] The tour list calculates rating, review count, next departure and seats left in one annotated query; a test with `assertNumQueries` proves it does not run one query per tour
- [ ] Tour detail has every field in the API file; `guide` and `meeting_point` are `null` when not set; `images` and `faqs` are sorted; `departures` are upcoming and scheduled
- [ ] An archived tour is `NOT_FOUND` for the public and visible to an admin
- [ ] Admin tour list includes archived tours and filters by `status` and `search`
- [ ] Create and update tour check every rule in the API file; a new price never changes existing bookings
- [ ] Archiving a tour removes it from the public list
- [ ] Image upload accepts JPG, PNG and WebP up to 5 MB, saves under `media/tours/`, and refuses other files with `VALIDATION_ERROR`
- [ ] Images, FAQs, guides and categories can be created, edited and deleted exactly as the API file says; a duplicate category name is `VALIDATION_ERROR`
- [ ] `languages` is stored as comma separated text and always sent as a list

### 3.5 Departures (5 calls and 2 helpers)

- [ ] `get_seats_taken` adds `traveller_count` of pending, approved and completed bookings only
- [ ] `is_booking_open` follows the `booking_open` rule: scheduled, before the deadline, seats left above 0, tour active
- [ ] `seats_taken`, `seats_left` and `booking_open` are worked out in one place and used by every response
- [ ] Departure list for a tour shows upcoming scheduled departures, soonest first
- [ ] Calendar needs `month` as `YYYY-MM`, leaves out cancelled departures, and includes `tour_title`
- [ ] Create checks that the start is in the future and the deadline is before the start
- [ ] Update refuses a capacity below the seats already held with `CAPACITY_CONFLICT` and the exact message in the API file
- [ ] Status `completed` turns every approved booking of the departure into completed through `complete_bookings_for_departure`, inside one `transaction.atomic()`; `cancelled` leaves bookings as they are

### 3.6 Coupons (4 calls and 2 helpers)

- [ ] `apply_coupon` refuses unknown, switched off, expired and used-up codes with `COUPON_INVALID` and a clear message for each
- [ ] The code is not case sensitive when checked, and is saved in capitals
- [ ] A percent discount is rounded to two decimals, half up; a fixed discount never takes the total below 0.00
- [ ] `mark_coupon_used` adds 1 to `times_used`
- [ ] `POST /coupons/validate` does not use the coupon up
- [ ] Admin create checks code length, uniqueness, type, value (at most 100 for percent), a future expiry and `max_uses`; update cannot change the code and can switch a coupon off

### 3.7 Reviews (3 calls)

- [ ] The tour review list is newest first with paging; `reviewer_name` is first name and last initial
- [ ] Create review uses `get_completed_booking_for_user`; `tour_id` comes from the booking
- [ ] `REVIEW_NOT_ALLOWED` (403) is raised for a booking that is not completed, not the caller's, or already reviewed
- [ ] The admin list filters by `tour_id` and `rating` and adds `user_id` and `tour_title`

### 3.8 Seed commands

- [ ] `seed_core` creates: 1 admin and 5 customers; 5 categories; 3 guides; 9 tours (1 archived); 2 images per tour; 2 to 3 FAQs per tour; departures (3 per active tour, plus the cancelled, full and closed test departures); the 5 coupons
- [ ] `seed_reviews` creates 3 reviews (ratings 5, 4, 3, one without a comment) and leaves 1 completed booking unreviewed
- [ ] `seed_all` runs `seed_core`, `seed_bookings`, `seed_reviews` in that order
- [ ] Every command can run twice with no duplicates and no error, supports `--reset`, makes all dates from now, uses password `Password123!`, and prints counts at the end
- [ ] `apps/seeds/constants.py` names the test departures and coupons so Member 3 never guesses

### 3.9 Member 2 final check

- [ ] The reset steps work: delete `db.sqlite3`, `migrate`, `seed_all`
- [ ] `site/progress/member-2.json` shows every task `done`
- [ ] All 33 calls pass every error case listed in the API file
- [ ] Every model, migration and `core` pull request from another member was reviewed within one working day
- [ ] No `STUB:` line is left anywhere
- [ ] The README explains setup, reset, seeded logins, the folder layout and how to run the tests
- [ ] `git tag v1.0` is created after the freeze

## 4. Member 3: Bookings, attendance, invoices and dashboard

**Owns:** `apps/bookings/` (except `models.py` and `migrations/`). Builds 12 calls and the `seed_bookings` command.

### 4.1 Before building

- [ ] Tests for the booking calls are written from the API file while Phase 0 is still in progress
- [ ] The proposed formats in section 6 of the API file are confirmed or changed by Member 3, and the change is recorded in the file

### 4.2 Customer booking calls (7 calls)

- [ ] **Quote** (`POST /bookings/quote`): saves nothing and does not count a coupon use; returns every field of `Quote`; `coupon_code` is `null` without a coupon
- [ ] **Create** (`POST /bookings`): runs in one `transaction.atomic()` and follows the six steps in the API file in the same order
- [ ] The price per person is copied from the tour; `subtotal`, `discount_amount` and `total_price` are `Decimal` and round half up to two decimals
- [ ] Seats are counted again inside the transaction with `get_seats_taken`; the message is "Only N seats are left."
- [ ] `BOOKING_CLOSED` is raised for an archived tour, a departure that is not scheduled, or a past deadline
- [ ] `booking_reference` is `KT-` plus 6 capital letters or digits, unique, with a retry on a clash
- [ ] `mark_coupon_used` runs only after the booking is saved; cancelling or rejecting does not give the use back
- [ ] The new booking has status `pending` and the full `Booking` shape; empty optional text is sent as `null`
- [ ] **My bookings:** only the caller's bookings, newest first, status filter, paging; `/bookings/my` is listed before `/bookings/<int:pk>`
- [ ] **Booking detail:** owner or admin; an admin gets `customer` and `attendance`; someone else's booking is `FORBIDDEN`
- [ ] **Cancel:** owner only; allowed from pending or approved before `cancel_deadline`; sets status, `status_reason` and `cancelled_at`; `can_cancel` becomes false; seats are free again
- [ ] Cancelling too late gives `CANCELLATION_NOT_ALLOWED`; cancelling from another status gives `INVALID_STATUS_CHANGE`
- [ ] `cancel_deadline` and `can_cancel` are correct in every Booking answer
- [ ] **Invoice:** owner or admin; a real PDF with reference, customer, tour, departure date, travellers, price per person, subtotal, discount, total in NZD; the file name is `invoice-<reference>.pdf`
- [ ] **Calendar:** owner only; a valid `.ics` with start time, tour title and meeting point; the file name is `<reference>.ics`

### 4.3 Admin calls (5 calls)

- [ ] **Admin list:** every filter works (`status`, `tour_id`, `departure_id`, `date_from`, `date_to`, `search`), with paging and no query per row
- [ ] **Status change:** only the allowed changes in the status table work; rejected, cancelled and completed are final; everything else is `INVALID_STATUS_CHANGE`; an admin may cancel after the customer's deadline; reject and cancel free the seats
- [ ] **Attendance list:** approved and completed bookings of one departure, with `attendance` as `present`, `absent` or `null`
- [ ] **Attendance update:** saves `marked_by` and `marked_at`; sending again changes the earlier mark; refused for bookings that are not approved or completed
- [ ] **Dashboard:** `active_tours`, `upcoming_departures`, all five keys in `bookings_by_status` (0 when none), and `total_value` from approved and completed bookings

### 4.4 Helpers for Member 2

- [ ] `complete_bookings_for_departure(departure)` changes only that departure's approved bookings to completed
- [ ] `get_completed_booking_for_user(booking_id, user)` returns the booking for its owner when it is completed, and otherwise lets the review call refuse it
- [ ] The real functions replace Member 2's stubs and the `STUB:` line is removed

### 4.5 Tests

- [ ] Each call has a success test and a test for each error listed in the API file
- [ ] **Overbooking test:** two requests for the last seats, only one succeeds and the other gets `SEATS_UNAVAILABLE`
- [ ] A test proves a coupon can be used up and that the next booking gets `COUPON_INVALID`
- [ ] A test proves every allowed and every refused status change

### 4.6 `seed_bookings`

- [ ] Creates exactly 16 bookings: 4 pending, 4 approved, 2 rejected (with `status_reason`), 2 cancelled (with reason and `cancelled_at`), 4 completed
- [ ] Mixes 1 to 4 travellers; 2 bookings use a coupon; some have dietary or accessibility notes
- [ ] Fills the "full" departure so all 4 seats are taken
- [ ] Every price is copied from the tour, with correct `subtotal`, `discount_amount` and `total_price`
- [ ] Creates 4 attendance records for the completed bookings (3 present, 1 absent, marked by the admin) and leaves 1 completed booking with none
- [ ] Safe to run twice, supports `--reset`, prints counts

### 4.7 Member 3 final check

- [ ] `site/progress/member-3.json` shows every task `done`
- [ ] All 12 calls pass every error case listed in the API file
- [ ] Booking creation cannot oversell a departure
- [ ] Reset and `seed_all` give 16 bookings and 4 attendance records on every laptop
- [ ] No `STUB:` line is left in the bookings app

## 5. Team success: the project is done when

- [ ] All 45 calls work, behave as the API file says and are used by the frontend
- [ ] Deleting `db.sqlite3`, then running `migrate` and `seed_all`, works on all three laptops with identical counts
- [ ] The team walked through these cases together and each worked: full departure, closed departure, archived tour, rejected booking, completed booking with a review, completed booking without a review
- [ ] A customer can: register, log in, search tours, see a calendar, get a quote, apply a coupon, book, see the booking, download the invoice and calendar, cancel within the rules, and review a completed tour
- [ ] An admin can: see the dashboard, manage tours, images, FAQs, guides, categories, departures and coupons, approve, reject and cancel bookings, mark attendance, complete a departure, and read reviews
- [ ] `python manage.py test` passes on a fresh clone
- [ ] No stub, no mock, no `print()`, no commented-out code
- [ ] `main` is tagged `v1.0` and the README is final
- [ ] The tracker at https://monikaritgithub.github.io/kiwi_trails/ shows 100% for the whole team
