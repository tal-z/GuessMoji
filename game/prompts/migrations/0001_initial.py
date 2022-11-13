# Generated by Django 4.1.2 on 2022-11-13 01:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ClueGuess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_id', models.IntegerField()),
                ('roommember_id', models.IntegerField()),
                ('clue', models.CharField(max_length=50)),
                ('guess', models.CharField(max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Prompt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=500)),
                ('category', models.CharField(blank=True, choices=[('Movie Titles', 'Movie Titles'), ('Song Titles', 'Song Titles'), ('Pop Culture', 'Pop Culture'), ('Miscellaneous', 'Miscellaneous'), ('Idioms', 'Idioms'), ('Places/Attractions', 'Places/Attractions'), ('Toys and Games', 'Toys and Games')], max_length=50, null=True)),
                ('hints', models.CharField(blank=True, max_length=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PromptClue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_id', models.IntegerField()),
                ('leader_id', models.IntegerField()),
                ('clue', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('prompt', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='prompts.prompt')),
            ],
            options={
                'unique_together': {('room_id', 'leader_id', 'prompt', 'clue')},
            },
        ),
    ]
