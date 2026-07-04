import uuid
import hashlib
from typing import List, Dict
from django.conf import settings
from django.db.models import F
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from research.models import MemoryEntry, SourceReliability
from django.contrib.auth import get_user_model

User = get_user_model()

class MemoryManager:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.collection_name = f"user_{user_id}_memories"
        # Initialize client with local storage path
        self.client = QdrantClient(path=settings.QDRANT_PATH)
        # Load embedding model
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

    def ensure_collection(self):
        """Creates collection if it doesn't already exist."""
        try:
            collections = [c.name for c in self.client.get_collections().collections]
            if self.collection_name not in collections:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
        except Exception as e:
            print(f"Error ensuring Qdrant collection: {e}")

    def embed(self, text: str) -> List[float]:
        """Embeds text into a 384-dimensional vector."""
        embedding = self.embedder.encode(text)
        return embedding.tolist()

    def store(self, content: str, metadata: dict) -> str:
        """Embeds content and stores it in Qdrant and SQLite databases."""
        self.ensure_collection()
        
        # Check deduplication first
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        existing = MemoryEntry.objects.filter(content_hash=content_hash).first()
        if existing:
            existing.access_count += 1
            existing.save()
            return existing.embedding_id

        point_id = str(uuid.uuid4())
        vector = self.embed(content)
        
        # Store in Qdrant
        payload = {
            "content": content,
            "user_id": self.user_id,
            **metadata
        }
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            ]
        )
        
        # Store metadata in Django PostgreSQL/SQLite database
        try:
            user = User.objects.get(id=self.user_id)
            MemoryEntry.objects.create(
                user=user,
                content=content,
                content_hash=content_hash,
                embedding_id=point_id,
                source_url=metadata.get("source_url", ""),
                source_tool=metadata.get("source_tool", "manual"),
                reliability_score=metadata.get("reliability_score", 0.5),
                topic_tags=metadata.get("topic_tags", [])
            )
        except Exception as e:
            print(f"Error saving MemoryEntry model: {e}")
            
        return point_id

    def retrieve(self, query: str, top_k: int = 5) -> List[dict]:
        """Retrieves top_k similar memory entries for a query."""
        self.ensure_collection()
        vector = self.embed(query)
        
        try:
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=vector,
                limit=top_k
            )
            
            hits = []
            for hit in search_result:
                payload = hit.payload
                # Update SQLite database hit counter
                point_id = hit.id
                MemoryEntry.objects.filter(embedding_id=point_id).update(
                    access_count=F('access_count') + 1
                )
                
                hits.append({
                    "content": payload.get("content", ""),
                    "source_url": payload.get("source_url", ""),
                    "source_tool": payload.get("source_tool", ""),
                    "reliability_score": payload.get("reliability_score", 0.5),
                    "topic_tags": payload.get("topic_tags", [])
                })
            return hits
        except Exception as e:
            print(f"Error retrieving from Qdrant: {e}")
            return []

    def deduplicate(self, content: str) -> bool:
        """Returns True if content has already been stored."""
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        return MemoryEntry.objects.filter(content_hash=content_hash).exists()

    def update_reliability(self, domain: str, positive: bool):
        """Learns and updates domain reliability scores over time."""
        if not domain:
            return
            
        source, created = SourceReliability.objects.get_or_create(domain=domain)
        source.times_cited += 1
        if not positive:
            source.times_flagged += 1
            
        # score = times_cited - times_flagged / times_cited
        if source.times_cited > 0:
            source.reliability_score = max(0.1, min(1.0, 1.0 - (source.times_flagged / source.times_cited)))
        
        source.save()
