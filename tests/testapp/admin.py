from django.contrib import admin

from fsm_admin_lite.mixins import FSMAdminMixin

from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(FSMAdminMixin, admin.ModelAdmin):
    list_display = ("id", "title", "state")

    fsm_fields = [
        "state",
    ]
