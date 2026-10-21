# Kiwi Trails: Database Design (Django + SQLite)

This is the database plan for the whole team. Member 2 owns it; Member 1 (frontend) and Member 3 (bookings) build to it. Change it only after the team agrees. It is written for **Django with SQLite**. Companion files: `kiwi-trails-02-api-design.md` (API calls), `kiwi-trails-03-coding-rules-and-folders.md` (folders and coding rules) and `kiwi-trails-04-success-criteria.md` (what "done" means for each member).

## 1. Who does what

| Table | Django model | App | Designed and migrated by | Seeded by |
| --- | --- | --- | --- | --- |
| `users` | `User` | `accounts` | Member 2 | Member 2 |
| `categories` | `Category` | `catalog` | Member 2 | Member 2 |
| `guides` | `Guide` | `catalog` | Member 2 | Member 2 |
| `tours` | `Tour` | `catalog` | Member 2 | Member 2 |
| `tour_images` | `TourImage` | `catalog` | Member 2 | Member 2 (Member 1 supplies the picture files in `media/seed/`) |
| `tour_faqs` | `TourFaq` | `catalog` | Member 2 | Member 2 |
| `departures` | `Departure` | `departures` | Member 2 | Member 2 |
| `coupons` | `Coupon` | `coupons` | Member 2 | Member 2 |
| `bookings` | `Booking` | `bookings` | Member 2 (model), Member 3 (API) | **Member 3** |
| `attendance` | `Attendance` | `bookings` | Member 2 (model), Member 3 (API) | **Member 3** |
| `reviews` | `Review` | `reviews` | Member 2 | Member 2, after Member 3 has seeded bookings |

Also created by Django, nobody edits them by hand: `authtoken_token` (login tokens), `django_migrations`, `django_content_type`, `auth_permission` and friends.

**Member 1** owns no tables. Member 1 supplies sample images and checks that the demo data shows correctly on every screen.

**Rule of one author for migrations:** Member 2 writes every model and every migration file, so there is never a migration clash. Member 3 asks Member 2 when a `bookings` or `attendance` column must change (see section 8).

## 2. SQLite and Django settings

```python
AUTH_USER_MODEL = "accounts.User"      # set before the very first migration
USE_TZ = True
TIME_ZONE = "UTC"                      # stored and sent in UTC; the frontend shows NZ time
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
```

- **One file per person.** `db.sqlite3` is in `.gitignore`. Nobody commits a database; everybody rebuilds the same data with the seed commands (section 7).
- **UTF-8:** SQLite stores UTF-8 text, so Taupō and Māori names are safe. Keep every file saved as UTF-8.
- **Money:** `DecimalField(max_digits=10, decimal_places=2)`. Do all price maths with Python `Decimal`, never `float`.
- **Enums:** `CharField` with `choices` (use `models.TextChoices`). The allowed words are in section 6.
- **Case:** SQLite compares text case-sensitively. Save emails in lower case and coupon codes in capitals (in the serializer and in `save()`).
- **One writer at a time:** SQLite locks the file while writing, and `select_for_update()` does nothing on SQLite. So creating a booking must run inside `transaction.atomic()`, re-count the seats inside that block, and keep it short. Member 3 writes a test that tries to book more seats than are left.
- **Foreign keys** are enforced by Django on SQLite. Do not turn them off.
- **Later move to PostgreSQL** is only a settings change if we avoid SQLite-only tricks. Do not write raw SQL.

## 3. Design type to Django field

| Design type | Django field |
| --- | --- |
| varchar(n) | `CharField(max_length=n)` |
| text | `TextField` |
| int | `IntegerField`, or `PositiveIntegerField` when it can never be negative |
| decimal(10,2) | `DecimalField(max_digits=10, decimal_places=2)` |
| decimal(9,6) | `DecimalField(max_digits=9, decimal_places=6)` |
| datetime | `DateTimeField` (aware, UTC) |
| boolean | `BooleanField` |
| enum | `CharField(choices=...)` |
| tinyint (rating) | `PositiveSmallIntegerField` with validators 1 to 5 |
| FK | `ForeignKey(..., on_delete=...)` |

Every model gets an automatic integer `id`. Every model sets `class Meta: db_table = "<plural name>"` so table names match this file.

## 4. Relationships and delete rules

| From | Link | To | `on_delete` | Why |
| --- | --- | --- | --- | --- |
| `tours.category_id` | many to one | `categories` | `PROTECT` | A used category cannot be deleted |
| `tours.guide_id` | many to one, optional | `guides` | `SET_NULL` | Removing a guide keeps the tour |
| `tour_images.tour_id` | many to one | `tours` | `CASCADE` | Images belong to the tour |
| `tour_faqs.tour_id` | many to one | `tours` | `CASCADE` | FAQs belong to the tour |
| `departures.tour_id` | many to one | `tours` | `PROTECT` | Tours are archived, not deleted |
| `bookings.departure_id` | many to one | `departures` | `PROTECT` | Bookings must survive |
| `bookings.user_id` | many to one | `users` | `PROTECT` | Same |
| `bookings.coupon_id` | many to one, optional | `coupons` | `PROTECT` | Coupons are switched off, not deleted |
| `attendance.booking_id` | one to one | `bookings` | `CASCADE` | One record per booking |
| `attendance.marked_by` | many to one | `users` | `PROTECT` | Keeps who marked it |
| `reviews.booking_id` | one to one | `bookings` | `PROTECT` | One review per booking |
| `reviews.user_id` | many to one | `users` | `PROTECT` | The reviewer |
| `reviews.tour_id` | many to one | `tours` | `PROTECT` | The reviewed tour |

Nothing important is ever deleted. Tours are archived, bookings are cancelled, coupons are switched off. Only images, FAQs and test data are deleted.

## 5. Table details

### users (`accounts.User`, custom user model)

| Column | Django field | Rules |
| --- | --- | --- |
| full\_name | `CharField(100)` | Required |
| email | `EmailField(150, unique=True)` | Required, saved in lower case, used to log in (`USERNAME_FIELD`) |
| password | Django's built-in password field | Holds the hash (this is the design's `password_hash`); never sent by the API |
| role | `CharField(choices)` | `customer` or `admin`, default `customer` |
| phone | `CharField(30, null=True, blank=True)` | Optional |
| is\_active | `BooleanField(default=True)` | Django needs it |
| created\_at, updated\_at | `DateTimeField(auto_now_add / auto_now)` | Set by the server |

### categories (`catalog.Category`)

| Column | Django field | Rules |
| --- | --- | --- |
| name | `CharField(60, unique=True)` | Required |

### guides (`catalog.Guide`)

| Column | Django field | Rules |
| --- | --- | --- |
| full\_name | `CharField(100)` | Required |
| bio | `TextField(blank=True)` | Biography |
| photo\_url | `CharField(255, null=True, blank=True)` | Optional |
| languages | `CharField(150, blank=True)` | Comma separated, e.g. `English, Te Reo Māori`; the API always sends a list |

### tours (`catalog.Tour`)

| Column | Django field | Rules |
| --- | --- | --- |
| title | `CharField(150)` | Required |
| description | `TextField` | Required |
| location | `CharField(100)` | e.g. `Taupō`; used by the search filter; index it |
| category | `ForeignKey(Category)` | Required |
| price\_per\_person | `DecimalField(10,2)` | NZD, above 0 |
| duration\_days | `PositiveIntegerField` | At least 1 |
| itinerary | `TextField` | Day-by-day plan |
| accessibility\_info | `TextField(blank=True)` | Shown on the tour page |
| visitor\_guidelines | `TextField(blank=True)` | Shown on the tour page |
| meeting\_point\_name | `CharField(150, blank=True)` | Text shown with the map |
| meeting\_lat, meeting\_lng | `DecimalField(9,6, null=True)` | Map position |
| guide | `ForeignKey(Guide, null=True)` | Optional |
| cancellation\_days | `PositiveIntegerField(default=7)` | Customers cancel until this many days before departure |
| status | `CharField(choices)` | `active` or `archived`, default `active`; index it |
| created\_at, updated\_at | `DateTimeField` | Set by the server |

### tour\_images (`catalog.TourImage`)

| Column | Django field | Rules |
| --- | --- | --- |
| tour | `ForeignKey(Tour)` | Required |
| image\_url | `CharField(255)` | Required; the file is saved under `media/tours/` |
| alt\_text | `CharField(150, blank=True)` | For screen readers |
| sort\_order | `IntegerField(default=0)` | Lowest first |

### tour\_faqs (`catalog.TourFaq`)

| Column | Django field | Rules |
| --- | --- | --- |
| tour | `ForeignKey(Tour)` | Required |
| question | `CharField(255)` | Required |
| answer | `TextField` | Required |
| sort\_order | `IntegerField(default=0)` | Lowest first |

### departures (`departures.Departure`)

| Column | Django field | Rules |
| --- | --- | --- |
| tour | `ForeignKey(Tour)` | Required |
| start\_datetime | `DateTimeField` | UTC; index it |
| capacity | `PositiveIntegerField` | Above 0; cannot go below the seats already held |
| booking\_deadline | `DateTimeField` | No new bookings after this; must be before `start_datetime` |
| status | `CharField(choices)` | `scheduled`, `completed` or `cancelled`, default `scheduled` |
| created\_at | `DateTimeField(auto_now_add)` | Set by the server |

**Not stored, worked out:** `seats_taken` = sum of `traveller_count` of bookings with status `pending`, `approved` or `completed`; `seats_left` = `capacity` − `seats_taken`; `booking_open` is true only when status is `scheduled`, now is before `booking_deadline`, `seats_left` > 0 and the tour is `active`. Write these once as model properties or a function in `departures/services.py`, and everyone calls that one place.

### coupons (`coupons.Coupon`)

| Column | Django field | Rules |
| --- | --- | --- |
| code | `CharField(30, unique=True)` | Required, saved in capitals, cannot change after creating |
| discount\_type | `CharField(choices)` | `percent` or `fixed` |
| discount\_value | `DecimalField(10,2)` | Percent 1 to 100, or an NZD amount |
| expires\_at | `DateTimeField` | After this the code is refused |
| max\_uses | `PositiveIntegerField(null=True)` | Empty means unlimited |
| times\_used | `PositiveIntegerField(default=0)` | Increased when a booking is created |
| is\_active | `BooleanField(default=True)` | Admins switch a coupon off here |

### bookings (`bookings.Booking`)

| Column | Django field | Rules |
| --- | --- | --- |
| booking\_reference | `CharField(20, unique=True)` | `KT-` plus 6 capital letters or digits, e.g. `KT-7H4K9Q`; retry if it already exists |
| user | `ForeignKey(User)` | The customer |
| departure | `ForeignKey(Departure)` | Required |
| traveller\_count | `PositiveIntegerField` | At least 1 |
| price\_per\_person | `DecimalField(10,2)` | Copied from the tour when booked, never changed |
| subtotal | `DecimalField(10,2)` | `price_per_person` × `traveller_count` |
| discount\_amount | `DecimalField(10,2, default=0)` | Default 0.00 |
| total\_price | `DecimalField(10,2)` | `subtotal` − `discount_amount` |
| coupon | `ForeignKey(Coupon, null=True)` | Optional |
| status | `CharField(choices)` | `pending`, `approved`, `rejected`, `cancelled`, `completed`; default `pending`; index it |
| pickup\_preference | `CharField(255, blank=True)` | Optional |
| dietary\_requirements | `CharField(255, blank=True)` | Optional |
| accessibility\_needs | `CharField(255, blank=True)` | Optional |
| status\_reason | `CharField(255, blank=True)` | Why it was rejected or cancelled |
| cancelled\_at | `DateTimeField(null=True)` | Optional |
| created\_at, updated\_at | `DateTimeField` | Set by the server |

The API sends empty optional text fields as `null`.

### reviews (`reviews.Review`)

| Column | Django field | Rules |
| --- | --- | --- |
| booking | `OneToOneField(Booking)` | Unique, so one review per booking |
| user | `ForeignKey(User)` | Must own the booking |
| tour | `ForeignKey(Tour)` | Required |
| rating | `PositiveSmallIntegerField` | Whole number 1 to 5 |
| comment | `TextField(blank=True)` | Optional, up to 1000 characters |
| created\_at | `DateTimeField(auto_now_add)` | Set by the server |

### attendance (`bookings.Attendance`)

| Column | Django field | Rules |
| --- | --- | --- |
| booking | `OneToOneField(Booking)` | One record per booking |
| status | `CharField(choices)` | `present` or `absent` |
| marked\_by | `ForeignKey(User)` | The admin who recorded it |
| marked\_at | `DateTimeField(auto_now)` | Set by the server |

## 6. Shared status values and rules

Everyone uses exactly these words, in lower case.

| Field | Allowed values | Default |
| --- | --- | --- |
| users.role | `customer`, `admin` | `customer` |
| tours.status | `active`, `archived` | `active` |
| departures.status | `scheduled`, `completed`, `cancelled` | `scheduled` |
| bookings.status | `pending`, `approved`, `rejected`, `cancelled`, `completed` | `pending` |
| coupons.discount\_type | `percent`, `fixed` | none |
| attendance.status | `present`, `absent` | none |

**Booking status changes.** Only these are allowed. Rejected, cancelled and completed are final. Anything else is refused with `INVALID_STATUS_CHANGE`.

| From | To | Who |
| --- | --- | --- |
| pending | approved | Admin |
| pending | rejected | Admin |
| pending | cancelled | Customer before the cancellation deadline, or admin |
| approved | cancelled | Customer before the cancellation deadline, or admin |
| approved | completed | Admin, or the system after the departure date |

Cancellation deadline = departure `start_datetime` minus the tour's `cancellation_days`.

**Seats:** pending, approved and completed bookings hold seats; rejected and cancelled release them.

## 7. Seed data: who seeds what

Seeding means filling a fresh database with the same demo records on every laptop, so all three members test the same data.

**Commands** (Django management commands, one file each; `seed_core`, `seed_reviews` and `seed_all` live in `apps/seeds/management/commands/`, and `seed_bookings` lives in `apps/bookings/management/commands/`):

| Command | Written and run by | What it creates | Needs first |
| --- | --- | --- | --- |
| `seed_core` | **Member 2** | users, categories, guides, tours, images, FAQs, departures, coupons | migrated empty database |
| `seed_bookings` | **Member 3** | bookings and attendance | `seed_core` |
| `seed_reviews` | **Member 2** | reviews | `seed_bookings` |
| `seed_all` | **Member 2** | runs the three above in that order | nothing |

Rules for every seed command:

- Safe to run twice: use `get_or_create` or `update_or_create` so it never makes duplicates.
- A `--reset` option deletes only that command's own rows, then recreates them.
- All dates are made from now (for example `now + 14 days`) so the demo data never goes out of date.
- Demo passwords are all `Password123!` (development only, never on a real server).
- Counts and names are printed at the end so you can check the result.

### seed\_core (Member 2)

| Table | Records |
| --- | --- |
| users | 1 admin `admin@kiwitrails.test`, and 5 customers (`aroha@`, `tane@`, `mei@`, `liam@`, `sione@kiwitrails.test`) |
| categories | Water, Hiking, Culture, Wildlife, Adventure |
| guides | 3, such as Hemi Walker (English, Te Reo Māori), with a short bio and photo path |
| tours | 9: Taupō Lake Cruise (NZ$249.00), Tongariro Alpine Crossing, Milford Sound Cruise, Waitomo Glowworm Caves, Rotorua Māori Cultural Evening, Abel Tasman Kayaking, Matamata Film Set Tour, Kaikōura Whale Watch, and **1 archived** tour. Mixed prices and 1 to 3 days. Taupō, Fiordland and similar names with macrons are used on purpose |
| tour\_images | 2 per tour, with `alt_text` |
| tour\_faqs | 2 to 3 per tour |
| departures | 3 per active tour: 1 past `completed`, 2 future `scheduled`. Plus these test cases: 1 `cancelled` future departure, 1 future departure with capacity 4 that Member 3 will fill ("full"), 1 future departure whose `booking_deadline` has already passed ("closed") |
| coupons | `SUMMER10` (10% off, active), `WELCOME20` (NZ$20 off, active), `EXPIRED5` (already expired), `SWITCHEDOFF` (`is_active` false), `ONEUSE` (`max_uses` 1, already used once) |

Member 2 keeps the names of the test departures in `apps/seeds/constants.py` so Member 3 can find them without guessing.

### seed\_bookings (Member 3)

| Table | Records |
| --- | --- |
| bookings | 16 spread over the five statuses: 4 `pending`, 4 `approved`, 2 `rejected` (with `status_reason`), 2 `cancelled` (with reason and `cancelled_at`), 4 `completed`. Mix of 1 to 4 travellers; 2 use a coupon; some with dietary or accessibility notes; enough bookings on the "full" departure to use all 4 seats; every price copied from the tour with correct `subtotal`, `discount_amount`, `total_price` |
| attendance | One record for each of the 4 completed bookings: 3 `present`, 1 `absent`, marked by the admin |

Member 3 also leaves 1 completed booking with no attendance record, to test the empty state.

### seed\_reviews (Member 2)

3 reviews on 3 of the 4 completed bookings (ratings 5, 4 and 3, one with no comment). The 4th completed booking stays unreviewed so the review form can be tested.

### Member 1

Puts 2 or 3 sample JPG or WebP pictures per tour in `media/seed/` (small files), plus guide photos. Uses the seeded data to check every screen: empty lists, a full departure, a closed departure, an archived tour, a rejected booking.

### Reset everything

```bash
rm db.sqlite3
python manage.py migrate
python manage.py seed_all
```

## 8. Migration rules

- Only Member 2 creates migration files. Commit the model change and its migration in the same commit.
- Never edit or delete a migration that is already on `main`. Add a new one.
- Need a new column? Open an issue or message Member 2 with the table, column, type and reason. After the change is merged everyone runs `git pull` then `python manage.py migrate`.
- If two migration files ever clash (same number), run `python manage.py makemigrations --merge` and commit the merge file.
- After every pull that includes a migration, run `migrate` before starting the server.

## 9. Database is done when

- [ ] `migrate` runs from an empty database with no error
- [ ] `seed_all` runs twice in a row with no error and no duplicates
- [ ] Every table, column, status word and rule above exists in the models
- [ ] Booking creation re-checks seats inside `transaction.atomic()`
- [ ] Member 1, Member 2 and Member 3 each ran the reset steps on their own laptop and got the same counts
