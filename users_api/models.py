from django.db import models

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=30)
    telegram_id = models.BigIntegerField(primary_key=True)
    telegram_username = models.CharField(max_length=200)
    sum_bought = models.IntegerField()
    def __str__(self) -> str:
        return self.name + ' @' + self.telegram_username
