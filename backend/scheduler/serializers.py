from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import ScheduledResearch

class ScheduledResearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledResearch
        fields = (
            'id', 'user', 'query_template', 'frequency',
            'is_active', 'last_run', 'next_run',
            'deliver_via_email', 'created_at'
        )
        read_only_fields = ('user', 'last_run', 'next_run', 'created_at')

    def create(self, validated_data):
        # Calculate next_run dynamically on creation
        freq = validated_data.get('frequency', 'daily')
        now = timezone.now()
        
        if freq == 'daily':
            next_run = now + timedelta(days=1)
        elif freq == 'weekly':
            next_run = now + timedelta(weeks=1)
        elif freq == 'monthly':
            next_run = now + timedelta(days=30)
        else:
            next_run = now + timedelta(days=1)
            
        validated_data['next_run'] = next_run
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # If frequency changed, recalculate next_run
        freq = validated_data.get('frequency', instance.frequency)
        if freq != instance.frequency:
            now = timezone.now()
            if freq == 'daily':
                instance.next_run = now + timedelta(days=1)
            elif freq == 'weekly':
                instance.next_run = now + timedelta(weeks=1)
            elif freq == 'monthly':
                instance.next_run = now + timedelta(days=30)
                
        return super().update(instance, validated_data)
