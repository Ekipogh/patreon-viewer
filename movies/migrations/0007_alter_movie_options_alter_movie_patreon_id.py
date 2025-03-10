# Generated by Django 4.2.19 on 2025-03-04 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0006_alter_genre_options_movie_patreon_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='movie',
            options={'ordering': ['patreon_id']},
        ),
        migrations.AlterField(
            model_name='movie',
            name='patreon_id',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
    ]
