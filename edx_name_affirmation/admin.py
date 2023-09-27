"""
Custom Django admin pages for Name Affirmation
"""

from django.contrib import admin

from edx_name_affirmation.models import VerifiedName, VerifiedNameConfig


@admin.register(VerifiedName)
class VerifiedNameAdmin(admin.ModelAdmin):
    """
    Admin for the VerifiedName Model
    """
    list_display = (
      'id', 'user', 'verified_name', 'verification_attempt_id', 'proctored_exam_attempt_id',
      'status', 'created', 'modified',
    )
    readonly_fields = ('id',)
    search_fields = ('user__username', 'verification_attempt_id', 'proctored_exam_attempt_id',)
    raw_id_fields = ('user', )


@admin.register(VerifiedNameConfig)
class VerifiedNameConfigAdmin(admin.ModelAdmin):
    """
    Admin for the VerifiedNameConfig Model
    """
    list_display = (
      'id', 'user', 'use_verified_name_for_certs', 'change_date',
    )
    readonly_fields = ('change_date',)
    search_fields = ('user__username',)
    raw_id_fields = ('user', )
