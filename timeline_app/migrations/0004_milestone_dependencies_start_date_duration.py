# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeline_app', '0003_alter_milestone_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='milestone',
            name='dependencies',
            field=models.ManyToManyField(blank=True, related_name='dependent_milestones', to='timeline_app.milestone'),
        ),
        migrations.AddField(
            model_name='milestone',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='milestone',
            name='duration',
            field=models.PositiveIntegerField(default=1, help_text='Duration in days'),
        ),]