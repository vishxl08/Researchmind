# Generated migration for research

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
            name='ResearchJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('query', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('done', 'Done'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('celery_task_id', models.CharField(blank=True, max_length=255)),
                ('max_iterations', models.IntegerField(default=10)),
                ('depth', models.CharField(choices=[('quick', 'Quick'), ('deep', 'Deep'), ('expert', 'Expert')], default='deep', max_length=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='research_jobs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'research_job',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SourceReliability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(max_length=255, unique=True)),
                ('reliability_score', models.FloatField(default=0.5)),
                ('times_cited', models.IntegerField(default=0)),
                ('times_flagged', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'source_reliability',
            },
        ),
        migrations.CreateModel(
            name='ResearchReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500)),
                ('executive_summary', models.TextField()),
                ('full_report_markdown', models.TextField()),
                ('sources', models.JSONField(default=list)),
                ('sub_questions', models.JSONField(default=list)),
                ('key_findings', models.JSONField(default=list)),
                ('contradictions_found', models.JSONField(default=list)),
                ('confidence_score', models.FloatField(default=0.0)),
                ('word_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('job', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='report', to='research.researchjob')),
            ],
            options={
                'db_table': 'research_report',
            },
        ),
        migrations.CreateModel(
            name='MemoryEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('content_hash', models.CharField(max_length=64, unique=True)),
                ('embedding_id', models.CharField(max_length=255)),
                ('source_url', models.URLField(blank=True, max_length=1000)),
                ('source_tool', models.CharField(max_length=50)),
                ('reliability_score', models.FloatField(default=0.5)),
                ('access_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_accessed', models.DateTimeField(auto_now=True)),
                ('topic_tags', models.JSONField(default=list)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memories', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'memory_entry',
                'ordering': ['-last_accessed'],
            },
        ),
        migrations.CreateModel(
            name='AgentStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step_type', models.CharField(choices=[('reason', 'Reason'), ('tool_call', 'Tool Call'), ('observe', 'Observe'), ('reflect', 'Reflect'), ('write', 'Write'), ('critique', 'Critique')], max_length=20)),
                ('step_number', models.IntegerField()),
                ('thought', models.TextField(blank=True)),
                ('tool_name', models.CharField(blank=True, max_length=100)),
                ('tool_input', models.JSONField(blank=True, null=True)),
                ('tool_output', models.TextField(blank=True)),
                ('tokens_used', models.IntegerField(default=0)),
                ('duration_ms', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='research.researchjob')),
            ],
            options={
                'db_table': 'agent_step',
                'ordering': ['step_number', 'created_at'],
            },
        ),
    ]
