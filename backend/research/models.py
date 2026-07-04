from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ResearchJob(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('done', 'Done'),
        ('failed', 'Failed')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='research_jobs')
    query = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    celery_task_id = models.CharField(max_length=255, blank=True)
    max_iterations = models.IntegerField(default=10)
    depth = models.CharField(
        max_length=10,
        choices=[('quick', 'Quick'), ('deep', 'Deep'), ('expert', 'Expert')],
        default='deep'
    )

    class Meta:
        db_table = 'research_job'
        ordering = ['-created_at', '-id']

    def __str__(self):
        return f"Job {self.id}: {self.query[:30]} ({self.status})"


class ResearchReport(models.Model):
    job = models.OneToOneField(ResearchJob, on_delete=models.CASCADE, related_name='report')
    title = models.CharField(max_length=500)
    executive_summary = models.TextField()
    full_report_markdown = models.TextField()
    sources = models.JSONField(default=list)          # [{url, title, reliability_score}]
    sub_questions = models.JSONField(default=list)
    key_findings = models.JSONField(default=list)
    contradictions_found = models.JSONField(default=list)
    confidence_score = models.FloatField(default=0.0)
    word_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'research_report'

    def __str__(self):
        return f"Report {self.id} for Job {self.job_id}: {self.title[:30]}"


class AgentStep(models.Model):
    STEP_TYPES = [
        ('reason', 'Reason'),
        ('tool_call', 'Tool Call'),
        ('observe', 'Observe'),
        ('reflect', 'Reflect'),
        ('write', 'Write'),
        ('critique', 'Critique')  # We added 'critique' from prompt's frontend mentions
    ]
    job = models.ForeignKey(ResearchJob, on_delete=models.CASCADE, related_name='steps')
    step_type = models.CharField(max_length=20, choices=STEP_TYPES)
    step_number = models.IntegerField()
    thought = models.TextField(blank=True)
    tool_name = models.CharField(max_length=100, blank=True)
    tool_input = models.JSONField(null=True, blank=True)
    tool_output = models.TextField(blank=True)
    tokens_used = models.IntegerField(default=0)
    duration_ms = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'agent_step'
        ordering = ['step_number', 'created_at']

    def __str__(self):
        return f"Step {self.step_number} ({self.step_type}) for Job {self.job_id}"


class MemoryEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memories')
    content = models.TextField()
    content_hash = models.CharField(max_length=64, unique=True)  # sha256, dedup
    embedding_id = models.CharField(max_length=255)              # Qdrant point ID
    source_url = models.URLField(blank=True, max_length=1000)    # Allow longer URLs
    source_tool = models.CharField(max_length=50)
    reliability_score = models.FloatField(default=0.5)
    access_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    topic_tags = models.JSONField(default=list)

    class Meta:
        db_table = 'memory_entry'
        ordering = ['-last_accessed']

    def __str__(self):
        return f"Memory {self.id}: {self.content[:30]}"


class SourceReliability(models.Model):
    domain = models.CharField(max_length=255, unique=True)
    reliability_score = models.FloatField(default=0.5)  # 0-1, learned from usage
    times_cited = models.IntegerField(default=0)
    times_flagged = models.IntegerField(default=0)

    class Meta:
        db_table = 'source_reliability'

    def __str__(self):
        return f"Source {self.domain} ({self.reliability_score})"
