# Generated by Django 4.2.16 on 2024-10-09 23:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wod20th", "0024_alter_note_unique_together_note_character_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="stat",
            name="stat_type",
            field=models.CharField(
                choices=[
                    ("attribute", "Attribute"),
                    ("ability", "Ability"),
                    ("advantage", "Advantage"),
                    ("background", "Background"),
                    ("lineage", "Lineage"),
                    ("discipline", "Discipline"),
                    ("gift", "Gift"),
                    ("sphere", "Sphere"),
                    ("rote", "Rote"),
                    ("art", "Art"),
                    ("splat", "Splat"),
                    ("edge", "Edge"),
                    ("discipline", "Discipline"),
                    ("path", "Path"),
                    ("power", "Power"),
                    ("other", "Other"),
                    ("virtue", "Virtue"),
                    ("vice", "Vice"),
                    ("merit", "Merit"),
                    ("flaw", "Flaw"),
                    ("trait", "Trait"),
                    ("skill", "Skill"),
                    ("knowledge", "Knowledge"),
                    ("knowlege-secondary", "Secondary Knowledge"),
                    ("telent-secondary", "Secondary Talent"),
                    ("skill-secondary", "Secondary Skill"),
                    ("talent", "Talent"),
                    ("specialty", "Specialty"),
                    ("other", "Other"),
                    ("physical", "Physical"),
                    ("social", "Social"),
                    ("mental", "Mental"),
                    ("personal", "Personal"),
                    ("supernatural", "Supernatural"),
                    ("moral", "Moral"),
                    ("inhuman", "Inhuman"),
                    ("temporary", "Temporary"),
                    ("dual", "Dual"),
                    ("renown", "Renown"),
                ],
                max_length=100,
            ),
        ),
    ]
