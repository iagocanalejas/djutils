import logging
from datetime import datetime

from django.db import models
from django.db.models import QuerySet

from djutils.utils.shortcuts import today
from pyutils.shortcuts import all_none

logger = logging.getLogger(__name__)


class DatableQuerySet(QuerySet):
    """Adds .schedule() method to QuerySet allowing quick filter by (date, day, week, month and year)"""

    def schedule(self, **kwargs):
        params = {}
        date = kwargs.pop("date", None)
        day = kwargs.pop("day", None)
        week = kwargs.pop("week", None)
        month = kwargs.pop("month", None)
        year = kwargs.pop("year", None)

        if all_none(date, day, week, month, year):
            # Default to current week
            week, year = today()[1], today()[0]

        if date:
            params[self.model.schedule_by] = date.date() if isinstance(date, datetime) else date
        if day:
            params[f"{self.model.schedule_by}__day"] = day
        if week:
            params[f"{self.model.schedule_by}__week"] = week
        if month:
            params[f"{self.model.schedule_by}__month"] = month
        if year:
            params[f"{self.model.schedule_by}__year"] = year

        return self.filter(**params)


class DatableManager(models.Manager):
    """Adds .schedule() method to Manager allowing quick filter by (date, day, week, month and year)"""

    def get_queryset(self):
        return DatableQuerySet(self.model, using=self._db)

    def schedule(self, **kwargs):
        return self.get_queryset().schedule(**kwargs)


class DatableModel(models.Model):
    """Set DatableManager as model manager allowing quick filter by (date, day, week, month and year)"""

    schedule_by = None
    objects = DatableManager()

    class Meta:
        abstract = True
