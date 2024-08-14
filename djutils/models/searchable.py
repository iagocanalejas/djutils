import operator
from functools import reduce

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import F, Func, Q, Value

from pyutils.lists import flatten
from pyutils.strings import closest_result, levenshtein_distance


class SearchableQuerySet(models.QuerySet):
    def closest_by_name(self, name: str, parts: list[str] | None = None):
        if not name:
            raise ValueError(f"invalid {name=}")
        name = name.upper()
        parts = parts if parts else name.split()

        q = self.all()

        # quick route, just an exact match
        values = self.filter(name__iexact=name)
        if values.count() == 1:
            return values.first()

        # go for similarity
        values = q.filter(reduce(operator.or_, [Q(name__icontains=n) | Q(joined_names__icontains=n) for n in parts]))

        matches = list(flatten(list(values.values_list("name", "known_names"))))
        closest, closest_distance = closest_result(name, matches) if matches else (None, 0)

        if closest and closest_distance > 0.4:  # bigger is better
            if closest_distance == 1.0:
                return self.get(Q(name=closest) | Q(known_names__contains=[closest]))

            avg_length = (len(closest) + len(name)) / 2
            normalized_levenshtein = levenshtein_distance(name, closest) / avg_length
            if normalized_levenshtein < 0.4:  # smaller is better
                return self.get(Q(name=closest) | Q(known_names__contains=[closest]))

        raise ObjectDoesNotExist


class SearchableManager(models.Manager):
    def get_queryset(self):
        return SearchableQuerySet(self.model).annotate(
            joined_names=Func(
                F("known_names"),
                Value(" "),
                function="array_to_string",
                output_field=models.CharField(),
            )
        )

    def closest_by_name(self, name: str, parts: list[str] | None = None):
        return self.get_queryset().closest_by_name(name, parts)


class SearchableModel(models.Model):
    """Adds a known_names value to a model"""

    known_names = ArrayField(default=list, blank=True, base_field=models.CharField(max_length=150))

    objects = models.Manager()
    searchable_objects = SearchableManager()

    class Meta:
        abstract = True
