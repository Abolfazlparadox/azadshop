# account/signals.py
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm
from .models import Membership
from product.models import Product
from blog.models import BlogPost
from comment.models import Comment
# from django.db import transaction

@receiver(user_logged_in)
def update_last_login_ip(sender, request, user, **kwargs):
    """Update last_login_ip when user logs in"""
    ip = get_client_ip(request)
    if ip and user.last_login_ip != ip:
        user.last_login_ip = ip
        user.save(update_fields=['last_login_ip'])

def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
@receiver(post_save, sender=Membership)
def grant_unit_officer_perms(sender, instance, created, **kwargs):
    if instance.role == Membership.Role.UNIT_OFFICER and instance.is_confirmed:
        user       = instance.user
        university = instance.university

        # Products in that university
        prods = Product.objects.filter(university=university)
        for p in prods:
            assign_perm('view_product',   user, p)
            assign_perm('change_product', user, p)
            assign_perm('delete_product', user, p)

        # BlogPosts in that university
        posts = BlogPost.objects.filter(university=university, is_published=True)
        for b in posts:
            assign_perm('view_blogpost',   user, b)
            assign_perm('change_blogpost', user, b)
            assign_perm('delete_blogpost', user, b)

        # Comments on those products & blogs
        comments = Comment.objects.filter(
            content_type__model__in=['product','blogpost'],
            object_id__in=list(prods.values_list('pk',flat=True))
                         + list(posts.values_list('pk',flat=True))
        )
        for c in comments:
            assign_perm('view_comment',   user, c)
            assign_perm('change_comment', user, c)
            assign_perm('delete_comment', user, c)