# Generated by Django 4.1.3 on 2022-11-20 21:50

import django_fsm
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies: list = []

    operations = [
        migrations.CreateModel(
            name="BlogPost",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("title", models.CharField(blank=True, max_length=200, null=True)),
                (
                    "state",
                    django_fsm.FSMField(
                        choices=[
                            ("created", "Created"),
                            ("reviewed", "Reviewed"),
                            ("published", "Published"),
                            ("hidden", "Hidden"),
                        ],
                        default="created",
                        max_length=50,
                        protected=True,
                    ),
                ),
            ],
        ),
    ]
