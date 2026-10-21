"""Constants and identifier mappings for database seeding.
Stores reference keys for seed departures and coupons across tests.
Provides test identifiers for teammate test suites.
"""

COUPON_SUMMER10 = "SUMMER10"
COUPON_WELCOME20 = "WELCOME20"
COUPON_EXPIRED5 = "EXPIRED5"
COUPON_SWITCHEDOFF = "SWITCHEDOFF"
COUPON_ONEUSE = "ONEUSE"

TEST_COUPONS = {
    "summer10": COUPON_SUMMER10,
    "welcome20": COUPON_WELCOME20,
    "expired5": COUPON_EXPIRED5,
    "switched_off": COUPON_SWITCHEDOFF,
    "one_use": COUPON_ONEUSE,
}

DEPARTURE_FULL = "full"
DEPARTURE_CLOSED = "closed"
DEPARTURE_CANCELLED = "cancelled"

TEST_DEPARTURES = {
    "full": DEPARTURE_FULL,
    "closed": DEPARTURE_CLOSED,
    "cancelled": DEPARTURE_CANCELLED,
}
