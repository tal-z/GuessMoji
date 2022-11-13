from django.db import migrations

import csv

def populate_prompts_from_csv(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Prompt = apps.get_model('prompts', 'Prompt')

    new_prompts = []

    with open("data/prompts.csv") as f:
        data = csv.DictReader(f)
        for prompt in data:
            new_prompts.append(
                Prompt(
                    message=prompt["Message"],
                    category=prompt["Category"],
                )
            )
        Prompt.objects.bulk_create(new_prompts)





class Migration(migrations.Migration):

    dependencies = [
        ('prompts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_prompts_from_csv),
    ]