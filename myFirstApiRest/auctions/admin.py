from django.contrib import admin

# Register your models here.
from .models import Auction, Category

admin.site.register(Auction)
admin.site.register(Category)
