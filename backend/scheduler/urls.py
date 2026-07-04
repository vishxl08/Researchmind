from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScheduledResearchViewSet

router = DefaultRouter()
router.register(r'jobs', ScheduledResearchViewSet, basename='scheduled-jobs')

urlpatterns = [
    path('', include(router.urls)),
]
