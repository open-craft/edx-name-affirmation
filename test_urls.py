from django.conf.urls import include, url

urlpatterns = [
  url(r'^', include('edx_name_affirmation.urls', namespace='edx_name_affirmation')),
]
