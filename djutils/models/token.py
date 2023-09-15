from django.db import models

from pyutils.shortcuts import generate_unique_code


class TokenModel(models.Model):
    _token_length = 8

    code = models.CharField(blank=False, max_length=_token_length)

    def save(self, *args, **kwargs):
        if not self.pk:
            # Set code on creation
            self.code = generate_unique_code(length=self._token_length)
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True
