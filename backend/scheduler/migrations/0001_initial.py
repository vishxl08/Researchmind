# Generated migration for scheduler

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduledResearch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('query_template', models.TextField()),
                ('frequency', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], max_length=10)),
                ('is_active', models.BooleanField(default=True)),
                ('last_run', models.DateTimeField(blank=True, null=True)),
                ('next_run', models.DateTimeField()),
                ('deliver_via_email', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scheduled_researches', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'scheduled_research',
                'ordering': ['-created_at'],
            },
        ),
    ]
