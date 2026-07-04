import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from research.models import (
    ResearchJob, ResearchReport, AgentStep, MemoryEntry, SourceReliability
)

User = get_user_model()


@pytest.mark.django_db
class TestResearchJobModel:
    """Test cases for ResearchJob model"""

    @pytest.fixture
    def user(self):
        return User.objects.create_user(username='testuser', password='pass123')

    def test_create_research_job(self, user):
        """Test creating a research job"""
        job = ResearchJob.objects.create(
            user=user,
            query='Test research query',
            status='pending'
        )
        assert job.query == 'Test research query'
        assert job.status == 'pending'
        assert job.max_iterations == 10
        assert job.depth == 'deep'

    def test_job_status_choices(self, user):
        """Test job status choices"""
        statuses = ['pending', 'running', 'done', 'failed']
        for status in statuses:
            job = ResearchJob.objects.create(
                user=user,
                query=f'Query for {status}',
                status=status
            )
            assert job.status == status

    def test_job_depth_choices(self, user):
        """Test job depth choices"""
        depths = ['quick', 'deep', 'expert']
        for depth in depths:
            job = ResearchJob.objects.create(
                user=user,
                query=f'Query for {depth}',
                depth=depth
            )
            assert job.depth == depth

    def test_job_ordering(self, user):
        """Test jobs are ordered by created_at descending"""
        job1 = ResearchJob.objects.create(user=user, query='First')
        job2 = ResearchJob.objects.create(user=user, query='Second')
        jobs = ResearchJob.objects.all()
        assert jobs[0].id == job2.id


@pytest.mark.django_db
class TestResearchReportModel:
    """Test cases for ResearchReport model"""

    @pytest.fixture
    def job(self):
        user = User.objects.create_user(username='testuser', password='pass123')
        return ResearchJob.objects.create(user=user, query='Test')

    def test_create_research_report(self, job):
        """Test creating a research report"""
        report = ResearchReport.objects.create(
            job=job,
            title='Test Report',
            executive_summary='Summary here',
            full_report_markdown='# Full Report',
            confidence_score=0.85
        )
        assert report.title == 'Test Report'
        assert report.confidence_score == 0.85
        assert report.word_count == 0

    def test_report_json_fields(self, job):
        """Test JSON fields in report"""
        sources = [{'url': 'http://example.com', 'title': 'Example', 'reliability': 0.8}]
        report = ResearchReport.objects.create(
            job=job,
            title='Test',
            executive_summary='Summary',
            full_report_markdown='# Report',
            sources=sources
        )
        assert report.sources == sources
        assert isinstance(report.sources, list)


@pytest.mark.django_db
class TestAgentStepModel:
    """Test cases for AgentStep model"""

    @pytest.fixture
    def job(self):
        user = User.objects.create_user(username='testuser', password='pass123')
        return ResearchJob.objects.create(user=user, query='Test')

    def test_create_agent_step(self, job):
        """Test creating an agent step"""
        step = AgentStep.objects.create(
            job=job,
            step_type='reason',
            step_number=1,
            thought='Thinking about the query'
        )
        assert step.step_type == 'reason'
        assert step.step_number == 1
        assert step.tokens_used == 0

    def test_step_types(self, job):
        """Test all step types"""
        types = ['reason', 'tool_call', 'observe', 'reflect', 'write', 'critique']
        for i, step_type in enumerate(types):
            step = AgentStep.objects.create(
                job=job,
                step_type=step_type,
                step_number=i
            )
            assert step.step_type == step_type

    def test_step_ordering(self, job):
        """Test steps are ordered by step_number"""
        step1 = AgentStep.objects.create(job=job, step_type='reason', step_number=2)
        step2 = AgentStep.objects.create(job=job, step_type='observe', step_number=1)
        steps = AgentStep.objects.all()
        assert steps[0].step_number == 1


@pytest.mark.django_db
class TestMemoryEntryModel:
    """Test cases for MemoryEntry model"""

    @pytest.fixture
    def user(self):
        return User.objects.create_user(username='testuser', password='pass123')

    def test_create_memory_entry(self, user):
        """Test creating a memory entry"""
        entry = MemoryEntry.objects.create(
            user=user,
            content='Important information',
            content_hash='abc123def456',
            embedding_id='point-1',
            source_tool='web_search'
        )
        assert entry.content == 'Important information'
        assert entry.access_count == 0
        assert entry.reliability_score == 0.5

    def test_memory_reliability_score(self, user):
        """Test memory entry reliability score"""
        entry = MemoryEntry.objects.create(
            user=user,
            content='Test',
            content_hash='hash1',
            embedding_id='point-1',
            source_tool='wikipedia',
            reliability_score=0.95
        )
        assert entry.reliability_score == 0.95

    def test_memory_topic_tags(self, user):
        """Test memory entry topic tags"""
        tags = ['python', 'machine-learning', 'ai']
        entry = MemoryEntry.objects.create(
            user=user,
            content='Test',
            content_hash='hash2',
            embedding_id='point-2',
            source_tool='arxiv',
            topic_tags=tags
        )
        assert entry.topic_tags == tags


@pytest.mark.django_db
class TestSourceReliabilityModel:
    """Test cases for SourceReliability model"""

    def test_create_source_reliability(self):
        """Test creating a source reliability record"""
        source = SourceReliability.objects.create(
            domain='example.com',
            reliability_score=0.75
        )
        assert source.domain == 'example.com'
        assert source.reliability_score == 0.75
        assert source.times_cited == 0

    def test_source_unique_domain(self):
        """Test domain uniqueness"""
        SourceReliability.objects.create(domain='unique.com', reliability_score=0.5)
        with pytest.raises(Exception):  # IntegrityError
            SourceReliability.objects.create(domain='unique.com', reliability_score=0.6)

    def test_update_source_metrics(self):
        """Test updating source reliability metrics"""
        source = SourceReliability.objects.create(domain='test.com')
        source.times_cited = 10
        source.times_flagged = 1
        source.reliability_score = 0.85
        source.save()
        
        updated = SourceReliability.objects.get(domain='test.com')
        assert updated.times_cited == 10
        assert updated.times_flagged == 1
        assert updated.reliability_score == 0.85
