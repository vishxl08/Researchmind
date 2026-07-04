import pytest
from django.contrib.auth import get_user_model
from scheduler.models import ScheduledResearch
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@pytest.mark.django_db
class TestScheduledResearchModel:
    """Test cases for ScheduledResearch model"""

    @pytest.fixture
    def user(self):
        return User.objects.create_user(username='testuser', password='pass123')

    def test_create_scheduled_research(self, user):
        """Test creating a scheduled research"""
        next_run = timezone.now() + timedelta(days=1)
        scheduled = ScheduledResearch.objects.create(
            user=user,
            query_template='Latest research on {topic}',
            frequency='daily',
            next_run=next_run
        )
        assert scheduled.query_template == 'Latest research on {topic}'
        assert scheduled.frequency == 'daily'
        assert scheduled.is_active is True

    def test_frequency_choices(self, user):
        """Test all frequency choices"""
        next_run = timezone.now() + timedelta(days=1)
        frequencies = ['daily', 'weekly', 'monthly']
        for freq in frequencies:
            scheduled = ScheduledResearch.objects.create(
                user=user,
                query_template=f'Query for {freq}',
                frequency=freq,
                next_run=next_run
            )
            assert scheduled.frequency == freq

    def test_scheduled_research_email_delivery(self, user):
        """Test email delivery flag"""
        next_run = timezone.now() + timedelta(days=1)
        scheduled = ScheduledResearch.objects.create(
            user=user,
            query_template='Test',
            frequency='weekly',
            next_run=next_run,
            deliver_via_email=True
        )
        assert scheduled.deliver_via_email is True

    def test_scheduled_research_last_run(self, user):
        """Test updating last run timestamp"""
        next_run = timezone.now() + timedelta(days=1)
        scheduled = ScheduledResearch.objects.create(
            user=user,
            query_template='Test',
            frequency='daily',
            next_run=next_run
        )
        assert scheduled.last_run is None
        
        scheduled.last_run = timezone.now()
        scheduled.save()
        
        updated = ScheduledResearch.objects.get(id=scheduled.id)
        assert updated.last_run is not None

    def test_scheduled_research_ordering(self, user):
        """Test scheduling is ordered by created_at descending"""
        next_run = timezone.now() + timedelta(days=1)
        scheduled1 = ScheduledResearch.objects.create(
            user=user, query_template='First', frequency='daily', next_run=next_run
        )
        scheduled2 = ScheduledResearch.objects.create(
            user=user, query_template='Second', frequency='daily', next_run=next_run
        )
        scheduled = ScheduledResearch.objects.all()
        assert scheduled[0].id == scheduled2.id
