from django.urls import path

from apps.ai.views import AIModelStatusView, AIPredictionView

urlpatterns = [
    path("predict/", AIPredictionView.as_view(), name="ai-predict"),
    path("status/", AIModelStatusView.as_view(), name="ai-status"),
]
