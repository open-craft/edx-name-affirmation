"""
URLs for edx_name_affirmation.
"""
from django.conf.urls import include, url

from edx_name_affirmation import views

app_name = u'edx_name_affirmation'

urlpatterns = [
    url(
        r'edx_name_affirmation/v1/verified_name$',
        views.VerifiedNameView.as_view(),
        name='verified_name'
    ),

    url(
        r'edx_name_affirmation/v1/verified_name/config$',
        views.VerifiedNameConfigView.as_view(),
        name='verified_name_config'
    ),

    url(r'^', include('rest_framework.urls', namespace='rest_framework')),
]
