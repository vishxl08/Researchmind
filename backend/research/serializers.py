from rest_framework import serializers
from .models import ResearchJob, ResearchReport, AgentStep, MemoryEntry, SourceReliability

class AgentStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentStep
        fields = '__all__'

class ResearchReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchReport
        fields = '__all__'

class ResearchJobSerializer(serializers.ModelSerializer):
    report = ResearchReportSerializer(read_only=True)
    steps_count = serializers.SerializerMethodField()

    class Meta:
        model = ResearchJob
        fields = (
            'id', 'user', 'query', 'status', 'created_at',
            'started_at', 'completed_at', 'celery_task_id',
            'max_iterations', 'depth', 'report', 'steps_count'
        )
        read_only_fields = ('user', 'status', 'created_at', 'started_at', 'completed_at', 'celery_task_id')

    def get_steps_count(self, obj):
        return obj.steps.count()

class MemoryEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = MemoryEntry
        fields = '__all__'
        read_only_fields = ('user', 'content_hash', 'embedding_id', 'created_at', 'last_accessed')

class SourceReliabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceReliability
        fields = '__all__'
