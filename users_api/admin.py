from django.contrib import admin
from .models import UserFree
from .models import Thing
from .models import CartObject
# Register your models here.

admin.site.register(UserFree)

admin.site.register(Thing)

admin.site.register(CartObject)
