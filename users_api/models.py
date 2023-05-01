from django.db import models
from asgiref.sync import sync_to_async
# Create your models here.
class UserFree(models.Model):
    name = models.CharField(max_length=30)
    telegram_id = models.BigIntegerField(primary_key=True)
    telegram_username = models.CharField(max_length=200)
    sum_bought = models.IntegerField()

    def __str__(self) -> str:
        return self.name + ' @' + self.telegram_username
    
    class Meta:
        verbose_name = 'Пользователь бота'
        verbose_name_plural = 'Пользователи бота'

class Thing(models.Model):
    category = models.IntegerField()
    subcategory = models.IntegerField()
    pic_id = models.CharField()
    name = models.CharField(max_length=70)
    description = models.TextField()
    price = models.BigIntegerField(default=0)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

class CartObject(models.Model):
    count = models.IntegerField()
    user = models.ForeignKey(UserFree, on_delete=models.CASCADE)
    thing = models.ForeignKey(Thing, on_delete=models.CASCADE)
    @sync_to_async
    def get_thing(self):
        return self.thing