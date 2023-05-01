from django.contrib import admin
from .models import UserFree
from .models import Thing
from .models import CartObject
# Register your models here.

class UserFreeAdmin(admin.ModelAdmin):
    list_display = ('name', 'telegram_username', 'sum_bought')

admin.site.register(UserFree, UserFreeAdmin)

class ThingAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'price')
admin.site.register(Thing, ThingAdmin)

# admin.site.register(CartObject)
