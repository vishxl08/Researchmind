from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ScheduledResearch(models.Model):
    FREQ_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_researches')
    query_template = models.TextField()
    frequency = models.CharField(max_length=10, choices=FREQ_CHOICES)
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField()
    deliver_via_email = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scheduled_research'
        ordering = ['-created_at', '-id']

    def __str__(self):
        return f"Scheduled {self.id}: {self.query_template[:30]} ({self.frequency})"
