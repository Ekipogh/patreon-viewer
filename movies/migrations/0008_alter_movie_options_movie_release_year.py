# Generated by Django 4.2.19 on 2025-03-05 00:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0007_alter_movie_options_alter_movie_patreon_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='movie',
            options={'ordering': ['-patreon_id']},
        ),
        migrations.AddField(
            model_name='movie',
            name='release_year',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
