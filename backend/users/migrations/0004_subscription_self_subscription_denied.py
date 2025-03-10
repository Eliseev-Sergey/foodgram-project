# Generated by Django 3.2 on 2023-11-13 21:03

from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20231101_1741'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.CheckConstraint(check=models.Q(user=django.db.models.expressions.F('author')), name='self_subscription_denied'),
        ),
    ]
