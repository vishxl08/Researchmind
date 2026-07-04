from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/research/(?P<job_id>\d+)/$', consumers.ResearchJobConsumer.as_asgi()),
]
