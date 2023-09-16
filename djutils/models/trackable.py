import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class CreationStampModel(models.Model):
    """Adds a creation stamp value to a model"""
    _editable_date = False

    creation_date = models.DateTimeField(null=False, blank=True, editable=_editable_date, default=timezone.now)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.creation_date = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class CreationAuditModel(CreationStampModel):
    """Adds creation audit values to a model"""

    created_by = models.ForeignKey(
        blank=False,
        null=False,
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_%(class)ss',
        related_query_name='created_%(class)s'
    )

    class Meta:
        abstract = True


class TraceableQuerySet(models.QuerySet):
    def delete(self):
        return super().update(to_date=timezone.now(), is_active=False)

    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(is_active=True)

    def dead(self):
        return self.filter(is_active=False)


class TraceableManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return TraceableQuerySet(self.model).filter(is_active=True)
        return TraceableQuerySet(self.model)

    def hard_delete(self):
        return self.get_queryset().hard_delete()


class TraceableModel(models.Model):
    """Adds fields to maintain a tracked history of instance deletions."""

    from_date = models.DateTimeField(null=False, blank=True, editable=False, default=timezone.now)
    to_date = models.DateTimeField(null=True, blank=True, default=None)
    is_active = models.BooleanField(null=False, blank=True, default=True, db_index=True)

    objects = TraceableManager()
    all_objects = TraceableManager(alive_only=False)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.to_date = timezone.now()
        self.is_active = False
        self.save()

    def save(self, *args, **kwargs):
        if not self.pk:
            # Set 'from_date' on first save
            self.from_date = timezone.now()

        if self.is_active and self.to_date is not None or not self.is_active and self.to_date is None:
            raise ValidationError({'non_field_errors': _("Set both or none: 'to_date' and 'is_active'")})

        super().save(*args, **kwargs)

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
