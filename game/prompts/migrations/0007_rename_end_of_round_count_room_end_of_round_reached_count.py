# Generated by Django 4.1.2 on 2022-10-27 13:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prompts', '0006_room_end_of_round_count'),
    ]

    operations = [
        migrations.RenameField(
            model_name='room',
            old_name='end_of_round_count',
            new_name='end_of_round_reached_count',
        ),
    ]
