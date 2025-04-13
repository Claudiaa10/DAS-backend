# Generated by Django 5.1.7 on 2025-04-10 08:33

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_bid'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='auctioneer',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='auctions', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='auction',
            name='rating',
            field=models.DecimalField(decimal_places=2, max_digits=3, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
    ]
