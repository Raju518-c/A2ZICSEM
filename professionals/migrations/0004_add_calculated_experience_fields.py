"""Adds two fields that exist on the current ProfessionalProfile model
but were never captured in any migration — industries_served and
total_career_experience_months. Both are system-managed with safe
defaults, so a plain AddField is correct here (unlike the drift fixes
elsewhere in this project, there's no legacy column to reconcile first).
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("professionals", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="professionalprofile",
            name="industries_served",
            field=models.JSONField(
                default=list,
                blank=True,
                help_text="Derived list of ReferenceValue codes (option_set=INDUSTRY) "
                "from all VERIFIED ProfessionalScope rows; system-managed.",
            ),
        ),
        migrations.AddField(
            model_name="professionalprofile",
            name="total_career_experience_months",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Union-merged calendar experience across all EmploymentRecord "
                "/ ProjectRecord rows, person-wide; never manually edited.",
            ),
        ),
    ]
