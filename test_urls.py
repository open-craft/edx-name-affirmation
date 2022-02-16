from django.urls import path, include

urlpatterns = [
  path('', include('edx_name_affirmation.urls', namespace='edx_name_affirmation')),
]
