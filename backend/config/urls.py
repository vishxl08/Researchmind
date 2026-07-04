from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from research.views import MemoryEntryViewSet, MemoryStatsView, DashboardStatsView

router = DefaultRouter()
router.register(r'memory/entries', MemoryEntryViewSet, basename='memory-entries')

urlpatterns = [
    path('', RedirectView.as_view(url='/api/', permanent=False), name='root-redirect'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/research/', include('research.urls')),
    path('api/scheduler/', include('scheduler.urls')),
    path('api/memory/stats/', MemoryStatsView.as_view(), name='memory-stats'),
    path('api/dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('api/', include(router.urls)),
]
