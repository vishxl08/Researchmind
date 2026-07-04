from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from agent.runner import run_agent
from scheduler.models import ScheduledResearch
from research.models import ResearchJob

@shared_task(bind=True, max_retries=2)
def run_research_job(self, job_id: int):
    """Executes a research agent run."""
    run_agent(job_id)

@shared_task
def run_scheduled_research():
    """Celery Beat periodic task checks ScheduledResearch and schedules due jobs."""
    now = timezone.now()
    due_items = ScheduledResearch.objects.filter(is_active=True, next_run__lte=now)
    
    for item in due_items:
        # Create a job
        job = ResearchJob.objects.create(
            user=item.user,
            query=item.query_template,
            status='pending',
            max_iterations=10,
            depth='deep'
        )
        
        # Calculate next run timestamp
        if item.frequency == 'daily':
            next_run = now + timedelta(days=1)
        elif item.frequency == 'weekly':
            next_run = now + timedelta(weeks=1)
        elif item.frequency == 'monthly':
            next_run = now + timedelta(days=30)
        else:
            next_run = now + timedelta(days=1)
            
        item.last_run = now
        item.next_run = next_run
        item.save()
        
        # Run Celery task
        run_research_job.delay(job.id)

@shared_task
def cleanup_old_jobs():
    """Cleans up research jobs and associated data older than 30 days."""
    cutoff = timezone.now() - timedelta(days=30)
    old_jobs = ResearchJob.objects.filter(created_at__lt=cutoff)
    count = old_jobs.count()
    old_jobs.delete()
    print(f"Cleaned up {count} old research jobs.")
