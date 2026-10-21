# Kiwi Trails: API Design by Member (Django)

This file says exactly which member builds which API call, how each call must behave, and what it sends and returns. Companion files: `kiwi-trails-01-database-design.md` (tables), `kiwi-trails-03-coding-rules-and-folders.md` (folders and coding rules) and `kiwi-trails-04-success-criteria.md` (what "done" means for each member). Every address starts with `/api/v1`. Section 6 (Member 3's calls) has formats that were missing in the original team plan, so they are **proposed** until Member 3 confirms them.

## Quick index of all 45 calls

Find a call here, then look for its heading further down. Every heading is followed by the same four parts: **who may call it**, **Request** (fields table and a real example), **Response** (a real example) and **Errors**.

| # | Method | Address (after `/api/v1`) | Who may call | View class | Built by | App |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | POST | `/auth/register` | Public | `RegisterView` | Member 2 | `accounts` |
| 2 | POST | `/auth/login` | Public | `LoginView` | Member 2 | `accounts` |
| 3 | POST | `/auth/logout` | Logged in | `LogoutView` | Member 2 | `accounts` |
| 4 | GET | `/users/me` | Logged in | `MeView` | Member 2 | `accounts` |
| 5 | PUT | `/users/me` | Logged in | `MeView` | Member 2 | `accounts` |
| 6 | GET | `/tours` | Public | `TourListView` | Member 2 | `catalog` |
| 7 | GET | `/tours/{id}` | Public | `TourDetailView` | Member 2 | `catalog` |
| 8 | GET | `/categories` | Public | `CategoryListView` | Member 2 | `catalog` |
| 9 | GET | `/guides/{id}` | Public | `GuideDetailView` | Member 2 | `catalog` |
| 10 | GET | `/admin/tours` | Admin | `AdminTourListCreateView` | Member 2 | `catalog` |
| 11 | POST | `/admin/tours` | Admin | `AdminTourListCreateView` | Member 2 | `catalog` |
| 12 | PUT | `/admin/tours/{id}` | Admin | `AdminTourUpdateView` | Member 2 | `catalog` |
| 13 | PATCH | `/admin/tours/{id}/status` | Admin | `AdminTourStatusView` | Member 2 | `catalog` |
| 14 | POST | `/admin/tours/{id}/images` | Admin | `AdminTourImageCreateView` | Member 2 | `catalog` |
| 15 | DELETE | `/admin/tour-images/{id}` | Admin | `AdminTourImageDeleteView` | Member 2 | `catalog` |
| 16 | POST | `/admin/tours/{id}/faqs` | Admin | `AdminFaqCreateView` | Member 2 | `catalog` |
| 17 | PUT | `/admin/faqs/{id}` | Admin | `AdminFaqDetailView` | Member 2 | `catalog` |
| 18 | DELETE | `/admin/faqs/{id}` | Admin | `AdminFaqDetailView` | Member 2 | `catalog` |
| 19 | POST | `/admin/guides` | Admin | `AdminGuideCreateView` | Member 2 | `catalog` |
| 20 | PUT | `/admin/guides/{id}` | Admin | `AdminGuideUpdateView` | Member 2 | `catalog` |
| 21 | POST | `/admin/categories` | Admin | `AdminCategoryCreateView` | Member 2 | `catalog` |
| 22 | GET | `/tours/{id}/departures` | Public | `TourDepartureListView` | Member 2 | `departures` |
| 23 | GET | `/departures/calendar` | Public | `DepartureCalendarView` | Member 2 | `departures` |
| 24 | POST | `/admin/tours/{id}/departures` | Admin | `AdminDepartureCreateView` | Member 2 | `departures` |
| 25 | PUT | `/admin/departures/{id}` | Admin | `AdminDepartureUpdateView` | Member 2 | `departures` |
| 26 | PATCH | `/admin/departures/{id}/status` | Admin | `AdminDepartureStatusView` | Member 2 | `departures` |
| 27 | GET | `/tours/{id}/reviews` | Public | `TourReviewListView` | Member 2 | `reviews` |
| 28 | POST | `/reviews` | Customer | `ReviewCreateView` | Member 2 | `reviews` |
| 29 | GET | `/admin/reviews` | Admin | `AdminReviewListView` | Member 2 | `reviews` |
| 30 | POST | `/coupons/validate` | Customer | `CouponValidateView` | Member 2 | `coupons` |
| 31 | GET | `/admin/coupons` | Admin | `AdminCouponListCreateView` | Member 2 | `coupons` |
| 32 | POST | `/admin/coupons` | Admin | `AdminCouponListCreateView` | Member 2 | `coupons` |
| 33 | PUT | `/admin/coupons/{id}` | Admin | `AdminCouponUpdateView` | Member 2 | `coupons` |
| 34 | POST | `/bookings/quote` | Customer | `BookingQuoteView` | Member 3 | `bookings` |
| 35 | POST | `/bookings` | Customer | `BookingCreateView` | Member 3 | `bookings` |
| 36 | GET | `/bookings/my` | Customer | `BookingMyListView` | Member 3 | `bookings` |
| 37 | GET | `/bookings/{id}` | Owner or admin | `BookingDetailView` | Member 3 | `bookings` |
| 38 | POST | `/bookings/{id}/cancel` | Owner | `BookingCancelView` | Member 3 | `bookings` |
| 39 | GET | `/bookings/{id}/invoice` | Owner or admin | `BookingInvoiceView` | Member 3 | `bookings` |
| 40 | GET | `/bookings/{id}/calendar` | Owner | `BookingCalendarView` | Member 3 | `bookings` |
| 41 | GET | `/admin/bookings` | Admin | `AdminBookingListView` | Member 3 | `bookings` |
| 42 | PATCH | `/admin/bookings/{id}/status` | Admin | `AdminBookingStatusView` | Member 3 | `bookings` |
| 43 | GET | `/admin/departures/{id}/attendance` | Admin | `AdminAttendanceListView` | Member 3 | `bookings` |
| 44 | PUT | `/admin/bookings/{id}/attendance` | Admin | `AdminAttendanceUpdateView` | Member 3 | `bookings` |
| 45 | GET | `/admin/dashboard` | Admin | `AdminDashboardView` | Member 3 | `bookings` |

## 1. How the API is built

- **Tools:** Django + Django REST Framework (DRF), `django-cors-headers` (so the frontend on another port can call the API), Pillow (image upload), ReportLab (PDF invoice). Member 2 pins versions in `requirements.txt`.
- **Shared base (`core` app, Member 2, built first, then frozen):** the success wrapper, the error handler, paging, permission classes, the token login check. Nobody else edits `core` without telling Member 2.
- **Login token:** DRF's built-in token (`authtoken`). Login deletes the person's old token and makes a new one; the token is valid 24 hours (`expires_at` = created + 24 h); logout deletes it. A custom `ExpiringTokenAuthentication` class in `core` refuses an old token with `UNAUTHENTICATED`.
- **Permission classes (in `core/permissions.py`):** `IsAuthenticated` (any logged in user), `IsCustomer`, `IsAdmin`, `IsOwnerOrAdmin` (object permission).
- **Order of checks, always the same:** token (401) → role (403) → item exists (404) → input valid (422) → business rule (409).
- **Server decides:** the server always re-checks permissions, seats and prices; the frontend only shows and collects.

### Rules for every call

| Item | Rule |
| --- | --- |
| Request body | JSON with `Content-Type: application/json` (image upload is `multipart/form-data`) |
| Protected calls | Header `Authorization: Bearer <token>` (set `keyword = "Bearer"` in the auth class) |
| Admin calls | Every address starting `/admin` needs role `admin` |
| Names | `snake_case`; a field with no value is `null`, never left out |
| Dates | ISO 8601 UTC, e.g. `2026-12-01T09:00:00Z` |
| Money | NZD, two decimals, e.g. `249.00` (send numbers, not strings) |
| Updates | `PUT` and `PATCH` change only the fields sent |
| `{id}` in the address | Always an integer; anything else is `NOT_FOUND` |
| Lists | `page` (from 1) and `page_size` (default 10, max 50); bad values are `VALIDATION_ERROR` |

**One item:** `{ "success": true, "data": { "id": 12 } }`

**List:** `{ "success": true, "data": { "items": [], "page": 1, "page_size": 10, "total": 42 } }`. A call marked *items* returns `{ "items": [] }` with no paging.

**Error:**

```json
{ "success": false, "error": { "code": "SEATS_UNAVAILABLE", "message": "Only 2 seats are left.", "fields": {} } }
```

`fields` names the wrong inputs, e.g. `{ "email": "Email is already used." }`.

| Error code | HTTP | When |
| --- | --- | --- |
| VALIDATION\_ERROR | 422 | A field is missing or wrong |
| UNAUTHENTICATED | 401 | No token or an expired token |
| FORBIDDEN | 403 | The role is not allowed |
| NOT\_FOUND | 404 | The item does not exist |
| EMAIL\_TAKEN | 409 | The email already has an account |
| SEATS\_UNAVAILABLE | 409 | Not enough seats left |
| BOOKING\_CLOSED | 409 | Past the booking deadline, departure cancelled or tour archived |
| CANCELLATION\_NOT\_ALLOWED | 409 | Past the cancellation deadline |
| INVALID\_STATUS\_CHANGE | 409 | The change is not in the status table |
| CAPACITY\_CONFLICT | 409 | Capacity set below the seats already held |
| COUPON\_INVALID | 422 | Unknown, expired, switched off or used up |
| REVIEW\_NOT\_ALLOWED | 403 | Booking not completed, not yours, or already reviewed |

Other codes: 200 OK, 201 Created, 400 Bad request.

## 2. Who builds what

| Group | Calls | Built by | Django app | Seeds the matching data |
| --- | --- | --- | --- | --- |
| Base (`core`) and Accounts | 5 | **Member 2** | `core`, `accounts` | Member 2 |
| Tours and content | 16 | **Member 2** | `catalog` | Member 2 |
| Departures | 5 | **Member 2** | `departures` | Member 2 |
| Reviews and coupons | 7 | **Member 2** | `reviews`, `coupons` | Member 2 |
| Bookings | 7 | **Member 3** | `bookings` | Member 3 |
| Admin bookings, attendance, dashboard | 5 | **Member 3** | `bookings` | Member 3 |
| All screens that call the API | 45 in total | **Member 1** | `frontend/` | supplies sample images |

### Calls between members (shared helpers)

To work at the same time, each member writes a small helper (a *service function*) that the other member calls. Agree the function names now; until the real one is merged, the caller uses a temporary stub with the same name.

| Helper | Written by | Called by | What it does |
| --- | --- | --- | --- |
| `departures.services.get_seats_taken(departure)` | Member 2 | Member 3 | Sum of `traveller_count` for pending, approved, completed bookings |
| `departures.services.is_booking_open(departure)` | Member 2 | Member 3 | The `booking_open` rule |
| `coupons.services.apply_coupon(code, subtotal)` | Member 2 | Member 3 | Returns the coupon, `discount_amount`, `new_total`; raises `CouponInvalid` |
| `coupons.services.mark_coupon_used(coupon)` | Member 2 | Member 3 | Adds 1 to `times_used` (call inside the booking transaction) |
| `bookings.services.complete_bookings_for_departure(departure)` | Member 3 | Member 2 | Changes a departure's `approved` bookings to `completed` |
| `bookings.services.get_completed_booking_for_user(booking_id, user)` | Member 3 | Member 2 | Used by `POST /reviews` to check ownership and status |
| `bookings.serializers.BookingSerializer` | Member 3 | Member 2 | Not needed by Member 2 (listed so nobody duplicates it) |

## 3. Data shapes

Every call below only names the shape it returns, so all calls that return a Booking return the same fields.

```json
User:     { "id": 3, "full_name": "Aroha Smith", "email": "aroha@example.com", "phone": "021 123 4567", "role": "customer", "created_at": "2026-10-01T02:15:00Z" }
Category: { "id": 2, "name": "Water" }
Guide:    { "id": 1, "full_name": "Hemi Walker", "bio": "Local guide for 12 years.", "photo_url": "/media/seed/guides/hemi.jpg", "languages": ["English", "Te Reo Māori"] }
Image:    { "id": 11, "image_url": "/media/seed/lake-cruise.jpg", "alt_text": "Boat on Lake Taupō", "sort_order": 1 }
FAQ:      { "id": 4, "question": "Is lunch included?", "answer": "Yes, a light lunch.", "sort_order": 1 }
Departure:{ "id": 8, "tour_id": 5, "start_datetime": "2026-12-01T20:00:00Z", "booking_deadline": "2026-11-29T20:00:00Z", "capacity": 12, "seats_taken": 6, "seats_left": 6, "booking_open": true, "status": "scheduled" }
Review:   { "id": 9, "tour_id": 5, "booking_id": 41, "rating": 5, "comment": "Wonderful day on the lake.", "reviewer_name": "Aroha S.", "created_at": "2026-12-03T01:00:00Z" }
Coupon:   { "id": 2, "code": "SUMMER10", "discount_type": "percent", "discount_value": 10.00, "expires_at": "2026-12-31T10:59:00Z", "max_uses": 100, "times_used": 12, "is_active": true }
Quote:    { "departure_id": 8, "traveller_count": 2, "price_per_person": 249.00, "subtotal": 498.00, "discount_amount": 49.80, "total_price": 448.20, "coupon_code": "SUMMER10", "seats_left": 6 }
AttendanceItem: { "booking_id": 41, "booking_reference": "KT-7H4K9Q", "customer_name": "Aroha Smith", "traveller_count": 2, "attendance": null }
Dashboard: { "active_tours": 8, "upcoming_departures": 14, "bookings_by_status": { "pending": 5, "approved": 21, "rejected": 2, "cancelled": 4, "completed": 9 }, "total_value": 9240.50 }
```

**Notes on the shapes**

- `Guide.languages` is stored as comma separated text but always sent as a list.
- `Departure`: `seats_taken` adds up `traveller_count` of pending, approved and completed bookings; `seats_left` = `capacity` − `seats_taken`; `booking_open` is true only when status is `scheduled`, now is before `booking_deadline`, `seats_left` > 0 and the tour is `active`.
- `Review.reviewer_name` is first name and last initial. The admin version also has `user_id` and `tour_title`.
- `Quote.coupon_code` is `null` when no coupon was used.
- `User.phone` is `null` if not given. The password is never returned.
- `Dashboard.total_value` adds `total_price` of approved and completed bookings.

**TourSummary** (one tour in a list)

```json
{ "id": 5, "title": "Taupō Lake Cruise", "location": "Taupō", "category_id": 2, "category": "Water", "price_per_person": 249.00, "duration_days": 1, "image_url": "/media/seed/lake-cruise.jpg", "average_rating": 4.6, "review_count": 18, "next_departure": "2026-12-01T20:00:00Z", "seats_left": 6, "status": "active" }
```

`image_url` is the first image or `null`. `average_rating` is `null` with no reviews. `next_departure` and `seats_left` describe the next departure open for booking, or are `null`.

**TourDetail** (one tour in full)

```json
{
  "id": 5, "title": "Taupō Lake Cruise", "description": "A relaxed cruise on the lake.", "location": "Taupō",
  "category_id": 2, "category": "Water", "price_per_person": 249.00, "duration_days": 1,
  "itinerary": "9:00 Board at the wharf. 12:00 Lunch on board.",
  "accessibility_info": "Wheelchair access to the main deck.", "visitor_guidelines": "Bring warm clothes.",
  "meeting_point": { "name": "Taupō Wharf", "lat": -38.6857, "lng": 176.0702 },
  "cancellation_days": 7, "status": "active",
  "images": [ <Image> ], "guide": <Guide>, "faqs": [ <FAQ> ],
  "average_rating": 4.6, "review_count": 18,
  "departures": [ <Departure> ]
}
```

`guide` and `meeting_point` are `null` when not set. `images` and `faqs` are sorted by `sort_order`. `departures` holds upcoming scheduled departures, soonest first.

**Booking**

```json
{
  "id": 41, "booking_reference": "KT-7H4K9Q", "status": "pending", "traveller_count": 2,
  "price_per_person": 249.00, "subtotal": 498.00, "discount_amount": 49.80, "total_price": 448.20,
  "coupon_code": "SUMMER10", "pickup_preference": "Hotel pickup", "dietary_requirements": "Vegetarian", "accessibility_needs": null,
  "status_reason": null, "cancelled_at": null, "can_cancel": true, "cancel_deadline": "2026-11-24T20:00:00Z",
  "tour": { "id": 5, "title": "Taupō Lake Cruise", "location": "Taupō" },
  "departure": { "id": 8, "start_datetime": "2026-12-01T20:00:00Z" },
  "created_at": "2026-10-21T02:00:00Z", "updated_at": "2026-10-21T02:00:00Z"
}
```

`cancel_deadline` = departure start minus the tour's `cancellation_days`. `can_cancel` is true when status is `pending` or `approved` and now is before `cancel_deadline`; the frontend uses it to show or hide the cancel button.

**BookingAdmin** = Booking plus `"customer": { "id": 3, "full_name": "Aroha Smith", "email": "aroha@example.com", "phone": "021 123 4567" }` and `"attendance": null` (`present`, `absent` or `null`).

## 4. Screens to calls (for Member 1)

| Screen | Calls |
| --- | --- |
| Register, login, profile | `POST /auth/register`, `POST /auth/login`, `POST /auth/logout`, `GET` and `PUT /users/me` |
| Tour list with filters | `GET /tours`, `GET /categories` |
| Tour page | `GET /tours/{id}`, `GET /tours/{id}/reviews`, `GET /guides/{id}` |
| Departure calendar | `GET /departures/calendar` |
| Booking form and price | `POST /bookings/quote`, `POST /coupons/validate`, `POST /bookings` |
| My bookings, booking page | `GET /bookings/my`, `GET /bookings/{id}`, `POST /bookings/{id}/cancel`, invoice and calendar downloads |
| Review form | `POST /reviews` |
| Admin dashboard | `GET /admin/dashboard` |
| Admin tours, images, FAQs, guides, categories | all `/admin/tours...`, `/admin/tour-images...`, `/admin/faqs...`, `/admin/guides...`, `/admin/categories` |
| Admin departures | `POST /admin/tours/{id}/departures`, `PUT` and `PATCH /admin/departures/{id}...` |
| Admin bookings and attendance | `GET /admin/bookings`, `PATCH /admin/bookings/{id}/status`, attendance calls |
| Admin coupons and reviews | `/admin/coupons`, `/admin/reviews` |

## 5. Member 2: calls to build

Every call below has the same parts in the same order: who may call it and which view class to write, then **Request** (fields table and a real example), **Response** (a real example), **Errors**. Examples use the seeded demo data. In code, helper functions are imported as `from apps.departures.services import get_seats_taken` (apps live in the `apps/` folder, see `kiwi-trails-03-coding-rules-and-folders.md`).

In every example, `Authorization: Bearer <token>` is the token from `POST /auth/login`. Responses are always inside `{ "success": true, "data": ... }`.

### 5.1 Accounts (app `accounts`)

#### POST `/auth/register`

Public · `RegisterView`. Creates a customer account; it does not log the person in.

**Request**

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `full_name` | text | yes | 2 to 100 characters |
| `email` | text | yes | valid email, not already used (saved in lower case) |
| `password` | text | yes | at least 8 characters |
| `phone` | text | no | any text up to 30 characters |

```http
POST /api/v1/auth/register
Content-Type: application/json

{ "full_name": "Aroha Smith", "email": "aroha@example.com", "password": "Password123!", "phone": "021 123 4567" }
```

**Response 201**

```json
{ "success": true, "data": { "id": 3, "full_name": "Aroha Smith", "email": "aroha@example.com", "phone": "021 123 4567", "role": "customer", "created_at": "2026-10-21T02:15:00Z" } }
```

**Errors:** `VALIDATION_ERROR` (422), `EMAIL_TAKEN` (409)

```json
{ "success": false, "error": { "code": "EMAIL_TAKEN", "message": "Email is already used.", "fields": { "email": "Email is already used." } } }
```

#### POST `/auth/login`

Public · `LoginView`. Deletes the person's old token and makes a new one valid for 24 hours.

**Request**

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `email` | text | yes | the account email |
| `password` | text | yes | the account password |

```http
POST /api/v1/auth/login
Content-Type: application/json

{ "email": "aroha@example.com", "password": "Password123!" }
```

**Response 200**

```json
{ "success": true, "data": { "token": "eyJ...", "expires_at": "2026-10-22T02:15:00Z", "user": { "id": 3, "full_name": "Aroha Smith", "email": "aroha@example.com", "phone": "021 123 4567", "role": "customer", "created_at": "2026-10-01T02:15:00Z" } } }
```

**Errors:** `VALIDATION_ERROR` (422), `UNAUTHENTICATED` (401). The message is the same for a wrong email and a wrong password, so nobody can guess which emails exist.

```json
{ "success": false, "error": { "code": "UNAUTHENTICATED", "message": "Email or password is wrong.", "fields": {} } }
```

#### POST `/auth/logout`

Logged in · `LogoutView`. Deletes the token.

**Request** (no body)

```http
POST /api/v1/auth/logout
Authorization: Bearer <token>
```

**Response 200**

```json
{ "success": true, "data": { "message": "Logged out" } }
```

**Errors:** `UNAUTHENTICATED` (401)

#### GET `/users/me`

Logged in · `MeView`. Own profile.

**Request** (no body)

```http
GET /api/v1/users/me
Authorization: Bearer <token>
```

**Response 200**

```json
{ "success": true, "data": { "id": 3, "full_name": "Aroha Smith", "email": "aroha@example.com", "phone": "021 123 4567", "role": "customer", "created_at": "2026-10-01T02:15:00Z" } }
```

**Errors:** `UNAUTHENTICATED` (401)

#### PUT `/users/me`

Logged in · `MeView`. Only the fields sent change. After a password change the old token stays valid (decision: keep simple).

**Request** (all fields optional)

| Field | Type | Rule |
| --- | --- | --- |
| `full_name` | text | 2 to 100 characters |
| `phone` | text or `null` | up to 30 characters; `null` clears it |
| `current_password` + `new_password` | text | send both together; new one at least 8 characters |

```http
PUT /api/v1/users/me
Authorization: Bearer <token>
Content-Type: application/json

{ "full_name": "Aroha Smith-Wiremu", "phone": null }
```

**Response 200**

```json
{ "success": true, "data": { "id": 3, "full_name": "Aroha Smith-Wiremu", "email": "aroha@example.com", "phone": null, "role": "customer", "created_at": "2026-10-01T02:15:00Z" } }
```

**Errors:** `VALIDATION_ERROR` (422, also for a wrong `current_password`), `UNAUTHENTICATED` (401)

```json
{ "success": false, "error": { "code": "VALIDATION_ERROR", "message": "Current password is wrong.", "fields": { "current_password": "Current password is wrong." } } }
```

### 5.2 Tours and content (app `catalog`)

#### GET `/tours`

Public · `TourListView`. Only `active` tours appear. Compute rating, next departure and seats with one annotated query, not one query per tour.

**Request** (query, all optional)

| Param | Type | Rule |
| --- | --- | --- |
| `search` | text | matches title and description |
| `location` | text | exact match, e.g. `Taupō` |
| `category_id` | integer | a category id |
| `min_price`, `max_price` | decimal | NZD |
| `sort` | text | `newest` (default), `price_asc`, `price_desc` |
| `page`, `page_size` | integer | page from 1; page\_size default 10, max 50 |

```http
GET /api/v1/tours?search=lake&category_id=2&sort=price_asc&page=1&page_size=10
```

**Response 200**

```json
{ "success": true, "data": { "items": [
  { "id": 5, "title": "Taupō Lake Cruise", "location": "Taupō", "category_id": 2, "category": "Water", "price_per_person": 249.00, "duration_days": 1, "image_url": "/media/seed/lake-cruise.jpg", "average_rating": 4.6, "review_count": 18, "next_departure": "2026-12-01T20:00:00Z", "seats_left": 6, "status": "active" }
], "page": 1, "page_size": 10, "total": 1 } }
```

`image_url` is the first image or `null`. `average_rating` is `null` with no reviews. `next_departure` and `seats_left` are `null` when no departure is open.

**Errors:** `VALIDATION_ERROR` (422), for example a `sort` value that does not exist

#### GET `/tours/{id}`

Public · `TourDetailView`.

**Request** (no body)

```http
GET /api/v1/tours/5
```

**Response 200**

```json
{ "success": true, "data": {
  "id": 5, "title": "Taupō Lake Cruise", "description": "A relaxed cruise on the lake.", "location": "Taupō",
  "category_id": 2, "category": "Water", "price_per_person": 249.00, "duration_days": 1,
  "itinerary": "9:00 Board at the wharf. 12:00 Lunch on board.",
  "accessibility_info": "Wheelchair access to the main deck.", "visitor_guidelines": "Bring warm clothes.",
  "meeting_point": { "name": "Taupō Wharf", "lat": -38.6857, "lng": 176.0702 },
  "cancellation_days": 7, "status": "active",
  "images": [ { "id": 11, "image_url": "/media/seed/lake-cruise.jpg", "alt_text": "Boat on Lake Taupō", "sort_order": 1 } ],
  "guide": { "id": 1, "full_name": "Hemi Walker", "bio": "Local guide for 12 years.", "photo_url": "/media/seed/guides/hemi.jpg", "languages": ["English", "Te Reo Māori"] },
  "faqs": [ { "id": 4, "question": "Is lunch included?", "answer": "Yes, a light lunch.", "sort_order": 1 } ],
  "average_rating": 4.6, "review_count": 18,
  "departures": [ { "id": 8, "tour_id": 5, "start_datetime": "2026-12-01T20:00:00Z", "booking_deadline": "2026-11-29T20:00:00Z", "capacity": 12, "seats_taken": 6, "seats_left": 6, "booking_open": true, "status": "scheduled" } ]
} }
```

`guide` and `meeting_point` are `null` when not set. `images` and `faqs` are sorted by `sort_order`. `departures` are upcoming scheduled ones, soonest first.

**Errors:** `NOT_FOUND` (404), also for an archived tour unless the caller is an admin

#### GET `/categories`

Public · `CategoryListView`.

**Request** (no body)

```http
GET /api/v1/categories
```

**Response 200** (*items*, no paging, sorted by name)

```json
{ "success": true, "data": { "items": [ { "id": 5, "name": "Adventure" }, { "id": 3, "name": "Culture" }, { "id": 2, "name": "Water" } ] } }
```

**Errors:** none

#### GET `/guides/{id}`

Public · `GuideDetailView`.

**Request** (no body)

```http
GET /api/v1/guides/1
```

**Response 200**

```json
{ "success": true, "data": { "id": 1, "full_name": "Hemi Walker", "bio": "Local guide for 12 years.", "photo_url": "/media/seed/guides/hemi.jpg", "languages": ["English", "Te Reo Māori"] } }
```

**Errors:** `NOT_FOUND` (404)

#### GET `/admin/tours`

Admin · `AdminTourListCreateView`. Same as `GET /tours` but includes archived tours.

**Request** (query, all optional): `status` (`active` or `archived`), `search` (text), `page`, `page_size`

```http
GET /api/v1/admin/tours?status=archived&page=1
Authorization: Bearer <admin token>
```

**Response 200**

```json
{ "success": true, "data": { "items": [
  { "id": 9, "title": "Old Hot Pools Visit", "location": "Rotorua", "category_id": 3, "category": "Culture", "price_per_person": 89.00, "duration_days": 1, "image_url": null, "average_rating": null, "review_count": 0, "next_departure": null, "seats_left": null, "status": "archived" }
], "page": 1, "page_size": 10, "total": 1 } }
```

**Errors:** `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

#### POST `/admin/tours`

Admin · `AdminTourListCreateView`. The new tour has status `active`.

**Request**

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `title` | text | yes | up to 150 characters |
| `description` | text | yes |  |
| `location` | text | yes | up to 100 characters |
| `category_id` | integer | yes | must exist |
| `price_per_person` | decimal | yes | above 0 |
| `duration_days` | integer | yes | at least 1 |
| `itinerary` | text | yes |  |
| `accessibility_info` | text | no |  |
| `visitor_guidelines` | text | no |  |
| `meeting_point_name` | text | no | up to 150 characters |
| `meeting_lat` | decimal | no | −90 to 90 |
| `meeting_lng` | decimal | no | −180 to 180 |
| `guide_id` | integer | no | must exist |
| `cancellation_days` | integer | no | default 7, at least 0 |

```http
POST /api/v1/admin/tours
Authorization: Bearer <admin token>
Content-Type: application/json

{ "title": "Waitomo Glowworm Caves", "description": "Float through the caves under the glowworms.", "location": "Waitomo", "category_id": 5, "price_per_person": 129.00, "duration_days": 1, "itinerary": "10:00 Meet at the visitor centre. 11:00 Cave tour.", "meeting_point_name": "Waitomo Visitor Centre", "meeting_lat": -38.2608, "meeting_lng": 175.1035, "guide_id": 1 }
```

**Response 201** (a full tour, same shape as `GET /tours/{id}`)

```json
{ "success": true, "data": {
  "id": 10, "title": "Waitomo Glowworm Caves", "description": "Float through the caves under the glowworms.", "location": "Waitomo",
  "category_id": 5, "category": "Adventure", "price_per_person": 129.00, "duration_days": 1,
  "itinerary": "10:00 Meet at the visitor centre. 11:00 Cave tour.",
  "accessibility_info": null, "visitor_guidelines": null,
  "meeting_point": { "name": "Waitomo Visitor Centre", "lat": -38.2608, "lng": 175.1035 },
  "cancellation_days": 7, "status": "active",
  "images": [], "guide": { "id": 1, "full_name": "Hemi Walker", "bio": "Local guide for 12 years.", "photo_url": "/media/seed/guides/hemi.jpg", "languages": ["English", "Te Reo Māori"] },
  "faqs": [], "average_rating": null, "review_count": 0, "departures": []
} }
```

**Errors:** `VALIDATION_ERROR` (422), `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

```json
{ "success": false, "error": { "code": "VALIDATION_ERROR", "message": "Some fields are wrong.", "fields": { "price_per_person": "Must be above 0.", "category_id": "Category does not exist." } } }
```

#### PUT `/admin/tours/{id}`

Admin · `AdminTourUpdateView`. Only the fields sent change. A new `price_per_person` never changes existing bookings.

**Request** (all fields optional, same fields and rules as the create call)

```http
PUT /api/v1/admin/tours/10
Authorization: Bearer <admin token>
Content-Type: application/json

{ "price_per_person": 139.00, "cancellation_days": 5 }
```

**Response 200** (the full updated tour, same shape as `GET /tours/{id}`)

```json
{ "success": true, "data": {
  "id": 10, "title": "Waitomo Glowworm Caves", "description": "Float through the caves under the glowworms.", "location": "Waitomo",
  "category_id": 5, "category": "Adventure", "price_per_person": 139.00, "duration_days": 1,
  "itinerary": "10:00 Meet at the visitor centre. 11:00 Cave tour.",
  "accessibility_info": null, "visitor_guidelines": null,
  "meeting_point": { "name": "Waitomo Visitor Centre", "lat": -38.2608, "lng": 175.1035 },
  "cancellation_days": 5, "status": "active",
  "images": [], "guide": { "id": 1, "full_name": "Hemi Walker", "bio": "Local guide for 12 years.", "photo_url": "/media/seed/guides/hemi.jpg", "languages": ["English", "Te Reo Māori"] },
  "faqs": [], "average_rating": null, "review_count": 0, "departures": []
} }
```

**Errors:** `VALIDATION_ERROR` (422), `NOT_FOUND` (404), `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

#### PATCH `/admin/tours/{id}/status`

Admin · `AdminTourStatusView`. An archived tour leaves the public list and refuses new bookings with `BOOKING_CLOSED`.

**Request**

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `status` | text | yes | `active` or `archived` |

```http
PATCH /api/v1/admin/tours/10/status
Authorization: Bearer <admin token>
Content-Type: application/json

{ "status": "archived" }
```

**Response 200**

```json
{ "success": true, "data": { "id": 10, "status": "archived" } }
```

**Errors:** `VALIDATION_ERROR` (422), `NOT_FOUND` (404), `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

#### POST `/admin/tours/{id}/images`

Admin · `AdminTourImageCreateView`. The only call that is not JSON: it sends `multipart/form-data`. Save the file under `media/tours/`.

**Request**

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `image` | file | yes | JPG, PNG or WebP, up to 5 MB |
| `alt_text` | text | no | up to 150 characters; describes the picture for screen readers |
| `sort_order` | integer | no | default 0, lowest first |

```http
POST /api/v1/admin/tours/5/images
Authorization: Bearer <admin token>
Content-Type: multipart/form-data; boundary=----kt

------kt
Content-Disposition: form-data; name="image"; filename="lake-cruise.jpg"
Content-Type: image/jpeg

<file bytes>
------kt
Content-Disposition: form-data; name="alt_text"

Boat on Lake Taupō
------kt--
```

**Response 201**

```json
{ "success": true, "data": { "id": 11, "image_url": "/media/tours/lake-cruise.jpg", "alt_text": "Boat on Lake Taupō", "sort_order": 0 } }
```

**Errors:** `VALIDATION_ERROR` (422, wrong file type or too large), `NOT_FOUND` (404), `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

#### DELETE `/admin/tour-images/{id}`

Admin · `AdminTourImageDeleteView`.

**Request** (no body)

```http
DELETE /api/v1/admin/tour-images/11
Authorization: Bearer <admin token>
```

**Response 200**

```json
{ "success": true, "data": { "deleted": true } }
```

**Errors:** `NOT_FOUND` (404), `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

#### POST `/admin/tours/{id}/faqs`

Admin · `AdminFaqCreateView`.

**Request**

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `question` | text | yes | up to 255 characters |
| `answer` | text | yes |  |
| `sort_order` | integer | no | default 0 |

```http
POST /api/v1/admin/tours/5/faqs
Authorization: Bearer <admin token>
Content-Type: application/json

{ "question": "Is lunch included?", "answer": "Yes, a light lunch.", "sort_order": 1 }
```

**Response 201**

```json
{ "success": true, "data": { "id": 4, "question": "Is lunch included?", "answer": "Yes, a light lunch.", "sort_order": 1 } }
```

**Errors:** `VALIDATION_ERROR` (422), `NOT_FOUND` (404), `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

#### PUT `/admin/faqs/{id}`

Admin · `AdminFaqDetailView`.

**Request** (all fields optional, same rules as create): `question`, `answer`, `sort_order`

```http
PUT /api/v1/admin/faqs/4
Authorization: Bearer <admin token>
Content-Type: application/json

{ "answer": "Yes, a light lunch and a hot drink." }
```

**Response 200**

```json
{ "success": true, "data": { "id": 4, "question": "Is lunch included?", "answer": "Yes, a light lunch and a hot drink.", "sort_order": 1 } }
```

**Errors:** `VALIDATION_ERROR` (422), `NOT_FOUND` (404), `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

#### DELETE `/admin/faqs/{id}`

Admin · `AdminFaqDetailView`.

**Request** (no body)

```http
DELETE /api/v1/admin/faqs/4
Authorization: Bearer <admin token>
```

**Response 200**

```json
{ "success": true, "data": { "deleted": true } }
```

**Errors:** `NOT_FOUND` (404), `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

#### POST `/admin/guides`

Admin · `AdminGuideCreateView`.

**Request**

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `full_name` | text | yes | up to 100 characters |
| `bio` | text | no |  |
| `photo_url` | text | no |  |
| `languages` | list of text | no | e.g. `["English", "Te Reo Māori"]` (stored as comma separated text) |

```http
POST /api/v1/admin/guides
Authorization: Bearer <admin token>
Content-Type: application/json

{ "full_name": "Hemi Walker", "bio": "Local guide for 12 years.", "photo_url": "/media/seed/guides/hemi.jpg", "languages": ["English", "Te Reo Māori"] }
```

**Response 201**

```json
{ "success": true, "data": { "id": 1, "full_name": "Hemi Walker", "bio": "Local guide for 12 years.", "photo_url": "/media/seed/guides/hemi.jpg", "languages": ["English", "Te Reo Māori"] } }
```

**Errors:** `VALIDATION_ERROR` (422), `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

#### PUT `/admin/guides/{id}`

Admin · `AdminGuideUpdateView`.

**Request** (all fields optional, same fields and rules as create)

```http
PUT /api/v1/admin/guides/1
Authorization: Bearer <admin token>
Content-Type: application/json

{ "bio": "Local guide for 13 years." }
```

**Response 200**

```json
{ "success": true, "data": { "id": 1, "full_name": "Hemi Walker", "bio": "Local guide for 13 years.", "photo_url": "/media/seed/guides/hemi.jpg", "languages": ["English", "Te Reo Māori"] } }
```

**Errors:** `VALIDATION_ERROR` (422), `NOT_FOUND` (404), `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

#### POST `/admin/categories`

Admin · `AdminCategoryCreateView`.

**Request**

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `name` | text | yes | up to 60 characters, not already used |

```http
POST /api/v1/admin/categories
Authorization: Bearer <admin token>
Content-Type: application/json

{ "name": "Food" }
```

**Response 201**

```json
{ "success": true, "data": { "id": 6, "name": "Food" } }
```

**Errors:** `VALIDATION_ERROR` (422, also when the name is already used), `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

### 5.3 Departures (app `departures`)

Every departure in a response has the same fields. `seats_taken` adds up `traveller_count` of pending, approved and completed bookings; `seats_left` = `capacity` − `seats_taken`; `booking_open` is true only when the status is `scheduled`, now is before `booking_deadline`, `seats_left` is above 0 and the tour is `active`.

#### GET `/tours/{id}/departures`

Public · `TourDepartureListView`. Upcoming departures with status `scheduled`, soonest first.

**Request** (no body)

```http
GET /api/v1/tours/5/departures
```

**Response 200** (*items*, no paging)

```json
{ "success": true, "data": { "items": [
  { "id": 8, "tour_id": 5, "start_datetime": "2026-12-01T20:00:00Z", "booking_deadline": "2026-11-29T20:00:00Z", "capacity": 12, "seats_taken": 6, "seats_left": 6, "booking_open": true, "status": "scheduled" }
] } }
```

**Errors:** `NOT_FOUND` (404)

#### GET `/departures/calendar`

Public · `DepartureCalendarView`. All departures in a month for the calendar screen. Cancelled departures are left out.

**Request** (query)

| Param | Type | Required | Rule |
| --- | --- | --- | --- |
| `month` | text | yes | `YYYY-MM`, e.g. `2026-12` |

```http
GET /api/v1/departures/calendar?month=2026-12
```

**Response 200**

```json
{ "success": true, "data": { "month": "2026-12", "items": [
  { "id": 8, "tour_id": 5, "tour_title": "Taupō Lake Cruise", "start_datetime": "2026-12-01T20:00:00Z", "booking_deadline": "2026-11-29T20:00:00Z", "capacity": 12, "seats_taken": 6, "seats_left": 6, "booking_open": true, "status": "scheduled" }
] } }
```

**Errors:** `VALIDATION_ERROR` (422, missing or wrong `month`)

#### POST `/admin/tours/{id}/departures`

Admin · `AdminDepartureCreateView`. The new departure has status `scheduled`.

**Request**

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `start_datetime` | datetime (UTC) | yes | in the future |
| `capacity` | integer | yes | at least 1 |
| `booking_deadline` | datetime (UTC) | yes | before `start_datetime` |

```http
POST /api/v1/admin/tours/5/departures
Authorization: Bearer <admin token>
Content-Type: application/json

{ "start_datetime": "2026-12-15T20:00:00Z", "capacity": 12, "booking_deadline": "2026-12-13T20:00:00Z" }
```

**Response 201**

```json
{ "success": true, "data": { "id": 15, "tour_id": 5, "start_datetime": "2026-12-15T20:00:00Z", "booking_deadline": "2026-12-13T20:00:00Z", "capacity": 12, "seats_taken": 0, "seats_left": 12, "booking_open": true, "status": "scheduled" } }
```

**Errors:** `VALIDATION_ERROR` (422), `NOT_FOUND` (404), `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

#### PUT `/admin/departures/{id}`

Admin · `AdminDepartureUpdateView`. Capacity cannot go below the seats already held.

**Request** (all fields optional, same rules as create): `start_datetime`, `capacity`, `booking_deadline`

```http
PUT /api/v1/admin/departures/8
Authorization: Bearer <admin token>
Content-Type: application/json

{ "capacity": 14 }
```

**Response 200**

```json
{ "success": true, "data": { "id": 8, "tour_id": 5, "start_datetime": "2026-12-01T20:00:00Z", "booking_deadline": "2026-11-29T20:00:00Z", "capacity": 14, "seats_taken": 6, "seats_left": 8, "booking_open": true, "status": "scheduled" } }
```

**Errors:** `VALIDATION_ERROR` (422), `CAPACITY_CONFLICT` (409), `NOT_FOUND` (404), `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

```json
{ "success": false, "error": { "code": "CAPACITY_CONFLICT", "message": "Capacity cannot be lower than the 6 seats already taken.", "fields": { "capacity": "Must be at least 6." } } }
```

#### PATCH `/admin/departures/{id}/status`

Admin · `AdminDepartureStatusView`. `completed` also turns every `approved` booking of this departure into `completed` (call `bookings.services.complete_bookings_for_departure`), which lets customers review the tour. `cancelled` leaves the bookings as they are; the admin handles each one with the booking status call. Do both changes in one `transaction.atomic()`.

**Request**

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `status` | text | yes | `completed` or `cancelled` |

```http
PATCH /api/v1/admin/departures/8/status
Authorization: Bearer <admin token>
Content-Type: application/json

{ "status": "completed" }
```

**Response 200**

```json
{ "success": true, "data": { "id": 8, "tour_id": 5, "start_datetime": "2026-12-01T20:00:00Z", "booking_deadline": "2026-11-29T20:00:00Z", "capacity": 14, "seats_taken": 6, "seats_left": 8, "booking_open": false, "status": "completed" } }
```

**Errors:** `VALIDATION_ERROR` (422), `NOT_FOUND` (404), `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

### 5.4 Reviews and coupons (apps `reviews`, `coupons`)

#### GET `/tours/{id}/reviews`

Public · `TourReviewListView`. Newest first. `reviewer_name` is the first name and last initial.

**Request** (query, optional): `page`, `page_size`

```http
GET /api/v1/tours/5/reviews?page=1&page_size=10
```

**Response 200**

```json
{ "success": true, "data": { "items": [
  { "id": 9, "tour_id": 5, "booking_id": 41, "rating": 5, "comment": "Wonderful day on the lake.", "reviewer_name": "Aroha S.", "created_at": "2026-12-03T01:00:00Z" }
], "page": 1, "page_size": 10, "total": 1 } }
```

**Errors:** `NOT_FOUND` (404)

#### POST `/reviews`

Customer · `ReviewCreateView`. `tour_id` is taken from the booking. Use `bookings.services.get_completed_booking_for_user` to check the booking.

**Request**

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `booking_id` | integer | yes | one of the caller's own bookings with status `completed` |
| `rating` | integer | yes | 1 to 5 |
| `comment` | text | no | up to 1000 characters |

```http
POST /api/v1/reviews
Authorization: Bearer <token>
Content-Type: application/json

{ "booking_id": 41, "rating": 5, "comment": "Wonderful day on the lake." }
```

**Response 201**

```json
{ "success": true, "data": { "id": 9, "tour_id": 5, "booking_id": 41, "rating": 5, "comment": "Wonderful day on the lake.", "reviewer_name": "Aroha S.", "created_at": "2026-12-03T01:00:00Z" } }
```

**Errors:** `VALIDATION_ERROR` (422), `REVIEW_NOT_ALLOWED` (403: not completed, not the caller's booking, or already reviewed), `UNAUTHENTICATED` (401)

```json
{ "success": false, "error": { "code": "REVIEW_NOT_ALLOWED", "message": "This booking has already been reviewed.", "fields": {} } }
```

#### GET `/admin/reviews`

Admin · `AdminReviewListView`. Newest first. The admin version of a review also has `user_id` and `tour_title`.

**Request** (query, all optional): `tour_id` (integer), `rating` (integer 1 to 5), `page`, `page_size`

```http
GET /api/v1/admin/reviews?tour_id=5&rating=5
Authorization: Bearer <admin token>
```

**Response 200**

```json
{ "success": true, "data": { "items": [
  { "id": 9, "tour_id": 5, "tour_title": "Taupō Lake Cruise", "booking_id": 41, "user_id": 3, "rating": 5, "comment": "Wonderful day on the lake.", "reviewer_name": "Aroha S.", "created_at": "2026-12-03T01:00:00Z" }
], "page": 1, "page_size": 10, "total": 1 } }
```

**Errors:** `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

#### POST `/coupons/validate`

Customer · `CouponValidateView`. Only checks the code; the coupon is used up when a booking is created, not here. Refuse when the code is unknown, expired, switched off (`is_active` false) or `times_used` has reached `max_uses`. A `fixed` discount never makes the total below 0.00. Round the discount to two decimals, half up.

**Request**

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `code` | text | yes | not case sensitive |
| `subtotal` | decimal | yes | above 0 |

```http
POST /api/v1/coupons/validate
Authorization: Bearer <token>
Content-Type: application/json

{ "code": "summer10", "subtotal": 498.00 }
```

**Response 200**

```json
{ "success": true, "data": { "code": "SUMMER10", "discount_type": "percent", "discount_value": 10.00, "discount_amount": 49.80, "new_total": 448.20 } }
```

**Errors:** `VALIDATION_ERROR` (422), `COUPON_INVALID` (422), `UNAUTHENTICATED` (401)

```json
{ "success": false, "error": { "code": "COUPON_INVALID", "message": "This coupon has expired.", "fields": { "code": "This coupon has expired." } } }
```

#### GET `/admin/coupons`

Admin · `AdminCouponListCreateView`. Newest first.

**Request** (query, optional): `page`, `page_size`

```http
GET /api/v1/admin/coupons?page=1
Authorization: Bearer <admin token>
```

**Response 200**

```json
{ "success": true, "data": { "items": [
  { "id": 2, "code": "SUMMER10", "discount_type": "percent", "discount_value": 10.00, "expires_at": "2026-12-31T10:59:00Z", "max_uses": 100, "times_used": 12, "is_active": true }
], "page": 1, "page_size": 10, "total": 1 } }
```

**Errors:** `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

#### POST `/admin/coupons`

Admin · `AdminCouponListCreateView`.

**Request**

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `code` | text | yes | 3 to 30 letters or digits, saved in capitals, not already used |
| `discount_type` | text | yes | `percent` or `fixed` |
| `discount_value` | decimal | yes | above 0; at most 100 for `percent` |
| `expires_at` | datetime (UTC) | yes | in the future |
| `max_uses` | integer | no | at least 1; empty means unlimited |

```http
POST /api/v1/admin/coupons
Authorization: Bearer <admin token>
Content-Type: application/json

{ "code": "WELCOME20", "discount_type": "fixed", "discount_value": 20.00, "expires_at": "2027-03-31T10:59:00Z", "max_uses": 50 }
```

**Response 201**

```json
{ "success": true, "data": { "id": 3, "code": "WELCOME20", "discount_type": "fixed", "discount_value": 20.00, "expires_at": "2027-03-31T10:59:00Z", "max_uses": 50, "times_used": 0, "is_active": true } }
```

**Errors:** `VALIDATION_ERROR` (422), `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

#### PUT `/admin/coupons/{id}`

Admin · `AdminCouponUpdateView`. The `code` cannot be changed.

**Request** (all fields optional): `discount_type`, `discount_value`, `expires_at`, `max_uses`, `is_active` (`false` switches the coupon off)

```http
PUT /api/v1/admin/coupons/3
Authorization: Bearer <admin token>
Content-Type: application/json

{ "is_active": false }
```

**Response 200**

```json
{ "success": true, "data": { "id": 3, "code": "WELCOME20", "discount_type": "fixed", "discount_value": 20.00, "expires_at": "2027-03-31T10:59:00Z", "max_uses": 50, "times_used": 0, "is_active": false } }
```

**Errors:** `VALIDATION_ERROR` (422), `NOT_FOUND` (404), `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

## 6. Member 3: calls to build (app `bookings`)

**Proposed formats.** The original team plan lists these calls and gives the Booking, BookingAdmin, Quote, AttendanceItem and Dashboard shapes, but not the request and error details. They are drafted from its rules. Member 3 confirms or changes them before building. In `bookings/urls.py` put `/bookings/my` **before** `/bookings/<int:pk>`.

`cancel_deadline` = departure start minus the tour's `cancellation_days`. `can_cancel` is true when the status is `pending` or `approved` and now is before `cancel_deadline`; the frontend uses it to show or hide the cancel button.

Every call in section 6 uses the same layout as section 5: who may call it, **Request**, **Response**, **Errors**.

### 6.1 Customer booking calls

#### POST `/bookings/quote`

Customer · `BookingQuoteView`. A price preview. Nothing is saved and no coupon use is counted.

**Request**

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `departure_id` | integer | yes | must exist |
| `traveller_count` | integer | yes | at least 1 |
| `coupon_code` | text | no | not case sensitive |

```http
POST /api/v1/bookings/quote
Authorization: Bearer <token>
Content-Type: application/json

{ "departure_id": 8, "traveller_count": 2, "coupon_code": "SUMMER10" }
```

**Response 200**

```json
{ "success": true, "data": { "departure_id": 8, "traveller_count": 2, "price_per_person": 249.00, "subtotal": 498.00, "discount_amount": 49.80, "total_price": 448.20, "coupon_code": "SUMMER10", "seats_left": 6 } }
```

`coupon_code` is `null` when no coupon was used.

**Errors:** `VALIDATION_ERROR` (422), `NOT_FOUND` (404), `SEATS_UNAVAILABLE` (409), `BOOKING_CLOSED` (409), `COUPON_INVALID` (422), `UNAUTHENTICATED` (401)

#### POST `/bookings`

Customer · `BookingCreateView`. Everything below runs inside one `transaction.atomic()`: (1) the tour is `active`, the departure is `scheduled` and now is before `booking_deadline`, else `BOOKING_CLOSED`; (2) re-count the seats with `get_seats_taken`, else `SEATS_UNAVAILABLE` ("Only N seats are left."); (3) if a coupon was sent, call `apply_coupon`, else `COUPON_INVALID`; (4) copy `price_per_person` from the tour and work out `subtotal`, `discount_amount`, `total_price`; (5) make a unique `booking_reference` (`KT-` plus 6 capitals or digits, retry on a clash); (6) save, then `mark_coupon_used`.

**Request**

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `departure_id` | integer | yes | must exist |
| `traveller_count` | integer | yes | at least 1 |
| `coupon_code` | text | no |  |
| `pickup_preference` | text | no | up to 255 characters |
| `dietary_requirements` | text | no | up to 255 characters |
| `accessibility_needs` | text | no | up to 255 characters |

```http
POST /api/v1/bookings
Authorization: Bearer <token>
Content-Type: application/json

{ "departure_id": 8, "traveller_count": 2, "coupon_code": "SUMMER10", "pickup_preference": "Hotel pickup", "dietary_requirements": "Vegetarian", "accessibility_needs": null }
```

**Response 201** (status `pending`)

```json
{ "success": true, "data": {
  "id": 41, "booking_reference": "KT-7H4K9Q", "status": "pending", "traveller_count": 2,
  "price_per_person": 249.00, "subtotal": 498.00, "discount_amount": 49.80, "total_price": 448.20,
  "coupon_code": "SUMMER10", "pickup_preference": "Hotel pickup", "dietary_requirements": "Vegetarian", "accessibility_needs": null,
  "status_reason": null, "cancelled_at": null, "can_cancel": true, "cancel_deadline": "2026-11-24T20:00:00Z",
  "tour": { "id": 5, "title": "Taupō Lake Cruise", "location": "Taupō" },
  "departure": { "id": 8, "start_datetime": "2026-12-01T20:00:00Z" },
  "created_at": "2026-10-21T02:00:00Z", "updated_at": "2026-10-21T02:00:00Z"
} }
```

**Errors:** `VALIDATION_ERROR` (422), `NOT_FOUND` (404), `SEATS_UNAVAILABLE` (409), `BOOKING_CLOSED` (409), `COUPON_INVALID` (422), `UNAUTHENTICATED` (401)

```json
{ "success": false, "error": { "code": "SEATS_UNAVAILABLE", "message": "Only 1 seat is left.", "fields": {} } }
```

#### GET `/bookings/my`

Customer · `BookingMyListView`. The caller's own bookings, newest first.

**Request** (query, all optional): `status` (`pending`, `approved`, `rejected`, `cancelled` or `completed`), `page`, `page_size`

```http
GET /api/v1/bookings/my?status=pending&page=1&page_size=10
Authorization: Bearer <token>
```

**Response 200**

```json
{ "success": true, "data": { "items": [ {
  "id": 41, "booking_reference": "KT-7H4K9Q", "status": "pending", "traveller_count": 2,
  "price_per_person": 249.00, "subtotal": 498.00, "discount_amount": 49.80, "total_price": 448.20,
  "coupon_code": "SUMMER10", "pickup_preference": "Hotel pickup", "dietary_requirements": "Vegetarian", "accessibility_needs": null,
  "status_reason": null, "cancelled_at": null, "can_cancel": true, "cancel_deadline": "2026-11-24T20:00:00Z",
  "tour": { "id": 5, "title": "Taupō Lake Cruise", "location": "Taupō" },
  "departure": { "id": 8, "start_datetime": "2026-12-01T20:00:00Z" },
  "created_at": "2026-10-21T02:00:00Z", "updated_at": "2026-10-21T02:00:00Z"
} ], "page": 1, "page_size": 10, "total": 1 } }
```

**Errors:** `VALIDATION_ERROR` (422), `UNAUTHENTICATED` (401)

#### GET `/bookings/{id}`

Owner or admin · `BookingDetailView`. An admin gets the BookingAdmin shape (the same fields plus `customer` and `attendance`, see 6.2).

**Request** (no body)

```http
GET /api/v1/bookings/41
Authorization: Bearer <token>
```

**Response 200** (as the owner)

```json
{ "success": true, "data": {
  "id": 41, "booking_reference": "KT-7H4K9Q", "status": "pending", "traveller_count": 2,
  "price_per_person": 249.00, "subtotal": 498.00, "discount_amount": 49.80, "total_price": 448.20,
  "coupon_code": "SUMMER10", "pickup_preference": "Hotel pickup", "dietary_requirements": "Vegetarian", "accessibility_needs": null,
  "status_reason": null, "cancelled_at": null, "can_cancel": true, "cancel_deadline": "2026-11-24T20:00:00Z",
  "tour": { "id": 5, "title": "Taupō Lake Cruise", "location": "Taupō" },
  "departure": { "id": 8, "start_datetime": "2026-12-01T20:00:00Z" },
  "created_at": "2026-10-21T02:00:00Z", "updated_at": "2026-10-21T02:00:00Z"
} }
```

**Errors:** `NOT_FOUND` (404), `FORBIDDEN` (403, someone else's booking), `UNAUTHENTICATED` (401)

#### POST `/bookings/{id}/cancel`

Owner · `BookingCancelView`. Cancels within the policy; the seats are free again.

**Request**

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `reason` | text | no | up to 255 characters |

```http
POST /api/v1/bookings/41/cancel
Authorization: Bearer <token>
Content-Type: application/json

{ "reason": "Change of plans" }
```

**Response 200** (status `cancelled`, `status_reason` and `cancelled_at` set, `can_cancel` false)

```json
{ "success": true, "data": {
  "id": 41, "booking_reference": "KT-7H4K9Q", "status": "cancelled", "traveller_count": 2,
  "price_per_person": 249.00, "subtotal": 498.00, "discount_amount": 49.80, "total_price": 448.20,
  "coupon_code": "SUMMER10", "pickup_preference": "Hotel pickup", "dietary_requirements": "Vegetarian", "accessibility_needs": null,
  "status_reason": "Change of plans", "cancelled_at": "2026-10-22T03:00:00Z", "can_cancel": false, "cancel_deadline": "2026-11-24T20:00:00Z",
  "tour": { "id": 5, "title": "Taupō Lake Cruise", "location": "Taupō" },
  "departure": { "id": 8, "start_datetime": "2026-12-01T20:00:00Z" },
  "created_at": "2026-10-21T02:00:00Z", "updated_at": "2026-10-22T03:00:00Z"
} }
```

**Errors:** `CANCELLATION_NOT_ALLOWED` (409, past `cancel_deadline`), `INVALID_STATUS_CHANGE` (409, not pending or approved), `NOT_FOUND` (404), `FORBIDDEN` (403), `UNAUTHENTICATED` (401)

```json
{ "success": false, "error": { "code": "CANCELLATION_NOT_ALLOWED", "message": "This booking can no longer be cancelled online.", "fields": {} } }
```

#### GET `/bookings/{id}/invoice`

Owner or admin · `BookingInvoiceView`. Returns a **file**, not JSON. The PDF shows reference, customer, tour, departure date, travellers, price per person, subtotal, discount and total in NZD.

**Request** (no body)

```http
GET /api/v1/bookings/41/invoice
Authorization: Bearer <token>
```

**Response 200**

```http
Content-Type: application/pdf
Content-Disposition: attachment; filename="invoice-KT-7H4K9Q.pdf"

<pdf bytes>
```

**Errors** (as JSON): `NOT_FOUND` (404), `FORBIDDEN` (403), `UNAUTHENTICATED` (401)

#### GET `/bookings/{id}/calendar`

Owner · `BookingCalendarView`. Returns a **file**, not JSON: an `.ics` calendar event with the start time, tour title and meeting point.

**Request** (no body)

```http
GET /api/v1/bookings/41/calendar
Authorization: Bearer <token>
```

**Response 200**

```http
Content-Type: text/calendar
Content-Disposition: attachment; filename="KT-7H4K9Q.ics"

BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:Taupō Lake Cruise
DTSTART:20261201T200000Z
LOCATION:Taupō Wharf
END:VEVENT
END:VCALENDAR
```

**Errors** (as JSON): `NOT_FOUND` (404), `FORBIDDEN` (403), `UNAUTHENTICATED` (401)

### 6.2 Admin bookings, attendance and dashboard

A **BookingAdmin** is a booking with two more fields: `customer` (`id`, `full_name`, `email`, `phone`) and `attendance` (`present`, `absent` or `null` when not recorded yet).

#### GET `/admin/bookings`

Admin · `AdminBookingListView`. Bookings with customer details, newest first.

**Request** (query, all optional)

| Param | Type | Rule |
| --- | --- | --- |
| `status` | text | one of the five booking statuses |
| `tour_id`, `departure_id` | integer |  |
| `date_from`, `date_to` | date | `YYYY-MM-DD`, on the departure start date |
| `search` | text | booking reference or customer name |
| `page`, `page_size` | integer | paging |

```http
GET /api/v1/admin/bookings?status=pending&search=KT-7H4K&page=1
Authorization: Bearer <admin token>
```

**Response 200**

```json
{ "success": true, "data": { "items": [ {
  "id": 41, "booking_reference": "KT-7H4K9Q", "status": "pending", "traveller_count": 2,
  "price_per_person": 249.00, "subtotal": 498.00, "discount_amount": 49.80, "total_price": 448.20,
  "coupon_code": "SUMMER10", "pickup_preference": "Hotel pickup", "dietary_requirements": "Vegetarian", "accessibility_needs": null,
  "status_reason": null, "cancelled_at": null, "can_cancel": true, "cancel_deadline": "2026-11-24T20:00:00Z",
  "tour": { "id": 5, "title": "Taupō Lake Cruise", "location": "Taupō" },
  "departure": { "id": 8, "start_datetime": "2026-12-01T20:00:00Z" },
  "created_at": "2026-10-21T02:00:00Z", "updated_at": "2026-10-21T02:00:00Z",
  "customer": { "id": 3, "full_name": "Aroha Smith", "email": "aroha@example.com", "phone": "021 123 4567" }, "attendance": null
} ], "page": 1, "page_size": 10, "total": 1 } }
```

**Errors:** `VALIDATION_ERROR` (422), `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

#### PATCH `/admin/bookings/{id}/status`

Admin · `AdminBookingStatusView`. Allowed changes only: pending → approved, rejected or cancelled; approved → cancelled or completed. Rejected, cancelled and completed are final. An admin may cancel after the customer's cancellation deadline. Rejecting or cancelling frees the seats.

**Request**

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `status` | text | yes | `approved`, `rejected`, `cancelled` or `completed` |
| `reason` | text | no | up to 255 characters; saved as `status_reason` |

```http
PATCH /api/v1/admin/bookings/41/status
Authorization: Bearer <admin token>
Content-Type: application/json

{ "status": "approved" }
```

**Response 200**

```json
{ "success": true, "data": {
  "id": 41, "booking_reference": "KT-7H4K9Q", "status": "approved", "traveller_count": 2,
  "price_per_person": 249.00, "subtotal": 498.00, "discount_amount": 49.80, "total_price": 448.20,
  "coupon_code": "SUMMER10", "pickup_preference": "Hotel pickup", "dietary_requirements": "Vegetarian", "accessibility_needs": null,
  "status_reason": null, "cancelled_at": null, "can_cancel": true, "cancel_deadline": "2026-11-24T20:00:00Z",
  "tour": { "id": 5, "title": "Taupō Lake Cruise", "location": "Taupō" },
  "departure": { "id": 8, "start_datetime": "2026-12-01T20:00:00Z" },
  "created_at": "2026-10-21T02:00:00Z", "updated_at": "2026-10-21T05:30:00Z",
  "customer": { "id": 3, "full_name": "Aroha Smith", "email": "aroha@example.com", "phone": "021 123 4567" }, "attendance": null
} }
```

**Errors:** `VALIDATION_ERROR` (422), `INVALID_STATUS_CHANGE` (409), `NOT_FOUND` (404), `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

```json
{ "success": false, "error": { "code": "INVALID_STATUS_CHANGE", "message": "A rejected booking cannot be approved.", "fields": {} } }
```

#### GET `/admin/departures/{id}/attendance`

Admin · `AdminAttendanceListView`. The `approved` and `completed` bookings of one departure.

**Request** (no body)

```http
GET /api/v1/admin/departures/8/attendance
Authorization: Bearer <admin token>
```

**Response 200** (*items*, no paging)

```json
{ "success": true, "data": { "items": [
  { "booking_id": 41, "booking_reference": "KT-7H4K9Q", "customer_name": "Aroha Smith", "traveller_count": 2, "attendance": null },
  { "booking_id": 43, "booking_reference": "KT-2M8XDA", "customer_name": "Tane Ngata", "traveller_count": 4, "attendance": "present" }
] } }
```

**Errors:** `NOT_FOUND` (404), `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

#### PUT `/admin/bookings/{id}/attendance`

Admin · `AdminAttendanceUpdateView`. Saves `marked_by` and `marked_at`; sending it again changes the earlier mark. Allowed only for `approved` or `completed` bookings.

**Request**

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `status` | text | yes | `present` or `absent` |

```http
PUT /api/v1/admin/bookings/41/attendance
Authorization: Bearer <admin token>
Content-Type: application/json

{ "status": "present" }
```

**Response 200**

```json
{ "success": true, "data": { "booking_id": 41, "booking_reference": "KT-7H4K9Q", "customer_name": "Aroha Smith", "traveller_count": 2, "attendance": "present" } }
```

**Errors:** `VALIDATION_ERROR` (422, also when the booking is not approved or completed), `NOT_FOUND` (404), `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

#### GET `/admin/dashboard`

Admin · `AdminDashboardView`. `active_tours` counts tours with status `active`; `upcoming_departures` counts scheduled departures that start in the future; `bookings_by_status` always has all five keys (0 when none); `total_value` adds `total_price` of approved and completed bookings.

**Request** (no body)

```http
GET /api/v1/admin/dashboard
Authorization: Bearer <admin token>
```

**Response 200**

```json
{ "success": true, "data": { "active_tours": 8, "upcoming_departures": 14, "bookings_by_status": { "pending": 5, "approved": 21, "rejected": 2, "cancelled": 4, "completed": 9 }, "total_value": 9240.50 } }
```

**Errors:** `UNAUTHENTICATED` (401), `FORBIDDEN` (403)

## 7. Member 1: how to use the API

- Keep one small file (for example `api.js`) that sends every request, adds the `Authorization: Bearer <token>` header, and turns the `{ success, data / error }` wrapper into data or an error. Screens never call `fetch` directly.
- Until a call is built, return a **mock**: copy the example JSON from this file exactly (same names, same `null` for empty). When the real call is merged, switch the mock off. Nothing else in the screens changes.
- Show `error.message` to the person; highlight inputs named in `error.fields`. Handle `UNAUTHENTICATED` by sending the person to the login screen.
- Use `can_cancel` to show the cancel button, `booking_open` and `seats_left` to enable the book button. Never work these out in the browser.
- Dates arrive in UTC; show them in New Zealand time. Money is NZD with two decimals.
- Test every screen against the seeded cases: full departure, closed departure, archived tour, rejected booking, completed booking with and without a review.

## 8. Questions to agree

These are my assumptions. Tick each one once the team agrees.

- [ ] Token: DRF token that lasts 24 hours, replaced on every login (instead of JWT).
- [ ] Cancelling or rejecting a booking does **not** give the coupon use back (`times_used` stays).
- [ ] Dashboard `total_value` counts approved **and** completed bookings. The original team plan's call table says only approved; the data shape says both, so this file follows the shape.
- [ ] Member 3's request and error details in section 6.
- [ ] Attendance can be recorded only for approved or completed bookings.
- [ ] The Member 2 and Member 3 helper names in section 2.

## 9. A call is done when

- [ ] It returns exactly the fields and `null` rules in this file, in the success wrapper
- [ ] Wrong or missing token gives 401, wrong role 403, missing item 404, bad input 422, rule clash 409, in that order
- [ ] Tests cover the success case and every error listed for it
- [ ] It works on the seeded data from a fresh `seed_all`
- [ ] The pull request is reviewed by one other member and merged with a correct commit message (see `kiwi-trails-03-coding-rules-and-folders.md`)
