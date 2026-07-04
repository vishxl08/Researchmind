from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResearchJobViewSet, ResearchReportViewSet, AgentStepListView

router = DefaultRouter()
router.register(r'jobs', ResearchJobViewSet, basename='jobs')
router.register(r'reports', ResearchReportViewSet, basename='reports')

urlpatterns = [
    path('', include(router.urls)),
    path('steps/<int:job_id>/', AgentStepListView.as_view(), name='agent-steps'),
]
