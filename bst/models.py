from django.db import models
from django.utils import timezone
import datetime
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MinValueValidator

class Measurement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique_for_date=True)
    date = models.DateField(default=datetime.date.today)
    weight = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])
    chest = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])
    waist = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])
    biceps = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])

    class Meta:
        ordering = ('date',)
        constraints = [
            models.UniqueConstraint(fields=['user', 'date'], name='unique day')
        ]

    # added just to prevent PyCharm warning - unresolved attribute reference 'objects' for class
    objects = models.Manager()

    # def get_absolute_url(self):
    #     return reverse('measure-detail', kwargs={'pk': self.pk})
