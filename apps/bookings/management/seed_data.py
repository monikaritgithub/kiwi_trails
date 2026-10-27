"""Stable sample booking definitions for the seed_bookings command."""

SEED_BOOKINGS = [
    # reference, customer, status, travellers, departure, coupon, attendance
    ("KT-SEED-001", "aroha", "pending", 2, "full", None, None),
    ("KT-SEED-002", "tane", "pending", 1, "future", None, None),
    ("KT-SEED-003", "mei", "pending", 3, "future", "SUMMER10", None),
    ("KT-SEED-004", "liam", "pending", 4, "future", None, None),
    ("KT-SEED-005", "sione", "approved", 2, "full", None, None),
    ("KT-SEED-006", "aroha", "approved", 1, "future", "WELCOME20", None),
    ("KT-SEED-007", "tane", "approved", 2, "future", None, None),
    ("KT-SEED-008", "mei", "approved", 3, "future", None, None),
    ("KT-SEED-009", "liam", "rejected", 1, "future", None, None),
    ("KT-SEED-010", "sione", "rejected", 2, "future", None, None),
    ("KT-SEED-011", "aroha", "cancelled", 2, "future", None, None),
    ("KT-SEED-012", "tane", "cancelled", 1, "future", None, None),
    ("KT-SEED-013", "mei", "completed", 2, "past", None, "present"),
    ("KT-SEED-014", "liam", "completed", 3, "past", None, "present"),
    ("KT-SEED-015", "sione", "completed", 1, "past", None, "absent"),
    ("KT-SEED-016", "aroha", "completed", 4, "past", None, None),
]

SEED_BOOKING_REFERENCES = tuple(row[0] for row in SEED_BOOKINGS)
