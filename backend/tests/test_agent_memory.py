import pytest
from unittest.mock import patch, MagicMock
from agent.memory import MemoryManager
from research.models import MemoryEntry, SourceReliability


@pytest.fixture
def memory_manager(test_user):
    """Fixture for memory manager with Qdrant/embedder mocked out"""
    with patch('agent.memory.QdrantClient'), patch('agent.memory.SentenceTransformer'):
        manager = MemoryManager(user_id=str(test_user.id))
        manager.client.get_collections.return_value.collections = []
        manager.embedder.encode.return_value = MagicMock(tolist=lambda: [0.1] * 384)
        return manager


@pytest.mark.django_db
class TestMemoryManagerInitialization:
    """Test memory manager initialization"""

    def test_memory_manager_init(self, memory_manager):
        """Test memory manager initializes"""
        assert memory_manager is not None

    @patch('agent.memory.SentenceTransformer')
    @patch('agent.memory.QdrantClient')
    def test_memory_manager_collection_creation(self, mock_client, mock_transformer, test_user):
        """Test memory manager creates collections when missing"""
        mock_instance = MagicMock()
        mock_instance.get_collections.return_value.collections = []
        mock_client.return_value = mock_instance

        manager = MemoryManager(user_id=str(test_user.id))
        manager.ensure_collection()

        mock_instance.create_collection.assert_called_once()


@pytest.mark.django_db
class TestMemoryAddition:
    """Test adding to memory"""

    def test_add_memory_entry(self, memory_manager, test_user):
        """Test adding a memory entry"""
        point_id = memory_manager.store(
            content='Test content',
            metadata={
                'source_url': 'http://example.com',
                'source_tool': 'web_search',
                'reliability_score': 0.8,
            }
        )

        assert point_id is not None
        assert MemoryEntry.objects.filter(embedding_id=point_id).exists()

    def test_add_memory_entry_deduplicates(self, memory_manager, test_user):
        """Test that storing the same content twice reuses the existing entry"""
        first_id = memory_manager.store('Duplicate content', {'source_tool': 'manual'})
        second_id = memory_manager.store('Duplicate content', {'source_tool': 'manual'})

        assert first_id == second_id
        assert MemoryEntry.objects.filter(embedding_id=first_id).count() == 1
        assert MemoryEntry.objects.get(embedding_id=first_id).access_count == 1


@pytest.mark.django_db
class TestMemorySearch:
    """Test searching memory"""

    def test_search_memory_success(self, memory_manager):
        """Test successful memory search"""
        hit = MagicMock()
        hit.id = 'point-1'
        hit.payload = {'content': 'Result 1', 'source_tool': 'web_search', 'reliability_score': 0.9}
        memory_manager.client.search.return_value = [hit]

        results = memory_manager.retrieve('test query', top_k=5)

        assert isinstance(results, list)
        assert results[0]['content'] == 'Result 1'

    def test_search_memory_empty(self, memory_manager):
        """Test memory search with no results"""
        memory_manager.client.search.return_value = []

        results = memory_manager.retrieve('nonexistent query xyz')

        assert isinstance(results, list)
        assert len(results) == 0


@pytest.mark.django_db
class TestMemoryDeduplication:
    """Test memory deduplication"""

    def test_memory_deduplication_new_content(self, memory_manager):
        """New content should not be flagged as a duplicate"""
        assert memory_manager.deduplicate('content never stored before') is False

    def test_memory_deduplication_existing_content(self, memory_manager):
        """Previously stored content should be flagged as a duplicate"""
        memory_manager.store('content to duplicate', {'source_tool': 'manual'})
        assert memory_manager.deduplicate('content to duplicate') is True


@pytest.mark.django_db
class TestSourceReliability:
    """Test source reliability learning"""

    def test_update_reliability_creates_source(self, memory_manager):
        """Updating reliability for a new domain creates a SourceReliability row"""
        memory_manager.update_reliability('example.com', positive=True)

        source = SourceReliability.objects.get(domain='example.com')
        assert source.times_cited == 1
        assert source.times_flagged == 0

    def test_update_reliability_flags_negative(self, memory_manager):
        """Negative feedback increments times_flagged and lowers the score"""
        memory_manager.update_reliability('unreliable.com', positive=False)

        source = SourceReliability.objects.get(domain='unreliable.com')
        assert source.times_flagged == 1
        assert source.reliability_score < 1.0
