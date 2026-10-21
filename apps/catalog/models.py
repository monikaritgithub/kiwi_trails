"""Catalog models for tours categories guides images and faqs.
Defines the database tables and relationships for tourist activities.
Follows the Kiwi Trails catalog domain design.
"""

from django.db import models


class TourStatus(models.TextChoices):
    ACTIVE = "active", "active"
    ARCHIVED = "archived", "archived"


class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)

    class Meta:
        db_table = "categories"

    def __str__(self):
        return self.name


class Guide(models.Model):
    full_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    photo_url = models.CharField(max_length=255, null=True, blank=True)
    languages = models.CharField(max_length=150, blank=True)

    class Meta:
        db_table = "guides"

    def __str__(self):
        return self.full_name


class Tour(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    location = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="tours")
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField()
    itinerary = models.TextField()
    accessibility_info = models.TextField(blank=True)
    visitor_guidelines = models.TextField(blank=True)
    meeting_point_name = models.CharField(max_length=150, blank=True)
    meeting_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    meeting_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    guide = models.ForeignKey(
        Guide,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tours",
    )
    cancellation_days = models.PositiveIntegerField(default=7)
    status = models.CharField(
        max_length=20,
        choices=TourStatus.choices,
        default=TourStatus.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tours"
        indexes = [
            models.Index(fields=["location"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.title


class TourImage(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="images")
    image_url = models.CharField(max_length=255)
    alt_text = models.CharField(max_length=150, blank=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = "tour_images"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"Image {self.id} for {self.tour.title}"


class TourFaq(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="faqs")
    question = models.CharField(max_length=255)
    answer = models.TextField()
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = "tour_faqs"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.question
