from rest_framework import viewsets, permissions
from .models import ScheduledResearch
from .serializers import ScheduledResearchSerializer

class ScheduledResearchViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduledResearchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ScheduledResearch.objects.filter(user=self.request.user)
