# comment/admin.py

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.admin import GenericTabularInline
from guardian.admin import GuardedModelAdmin

from .models import Comment


class CommentInline(GenericTabularInline):
    """
    Inline for replies under parent comments.
    """
    model = Comment
    ct_field = 'content_type'
    ct_fk_field = 'object_id'
    extra = 0
    readonly_fields = ('user', 'content', 'rating', 'likes', 'is_approved', 'created_at')
    fields = ('user', 'content', 'rating', 'likes', 'is_approved', 'created_at')
    show_change_link = True


@admin.register(Comment)
class CommentAdmin(GuardedModelAdmin):
    """
    Guardian-enabled admin for Comment model.
    Only shows objects user has permission to view/change.
    """
    list_display = (
        'short_content', 'user', 'content_object',
        'rating', 'likes', 'is_approved', 'created_at'
    )
    list_filter = ('is_approved', 'rating', 'content_type', 'created_at')
    search_fields = ('content', 'user__username', 'user__email')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    actions = ['approve_comments', 'disapprove_comments']
    list_select_related = ('user',)

    inlines = [CommentInline]

    fieldsets = (
        (None, {
            'fields': (
                'user', 'content_type', 'object_id',
                'parent', 'content', 'rating', 'likes'
            )
        }),
        (_('Status'), {
            'fields': ('is_approved',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def short_content(self, obj):
        text = obj.content or ''
        return text if len(text) <= 50 else text[:47] + '...'
    short_content.short_description = _('متن دیدگاه')

    @admin.action(description=_("تأیید دیدگاه‌های انتخاب‌شده"))
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, _('%(count)d دیدگاه تأیید شد.') % {'count': updated})

    @admin.action(description=_("رد دیدگاه‌های انتخاب‌شده"))
    def disapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, _('%(count)d دیدگاه رد شد.') % {'count': updated})
