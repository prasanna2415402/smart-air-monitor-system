import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base providing created/updated timestamps for every model."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """Abstract base using a UUID primary key instead of an integer id."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
