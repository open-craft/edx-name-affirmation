"""
URLs for edx_name_affirmation.
"""

from django.urls import include, path, re_path

from edx_name_affirmation import views

app_name = 'edx_name_affirmation'

urlpatterns = [
    path(
        'edx_name_affirmation/v1/verified_name', views.VerifiedNameView.as_view(),
        name='verified_name'
    ),

    re_path(
        r'edx_name_affirmation/v1/verified_name/(?P<verified_name_id>\d+)$',
        views.VerifiedNameView.as_view(), name='verified_name_by_id'
    ),

    path(
        'edx_name_affirmation/v1/verified_name/history', views.VerifiedNameHistoryView.as_view(),
        name='verified_name_history'
    ),

    path(
        'edx_name_affirmation/v1/verified_name/config', views.VerifiedNameConfigView.as_view(),
        name='verified_name_config'
    ),

    path('', include('rest_framework.urls', namespace='rest_framework')),
]
