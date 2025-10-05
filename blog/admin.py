from django.contrib import admin, messages
from django.utils.text import slugify
from django.urls import path
from django.shortcuts import redirect, get_object_or_404
from django.utils.html import format_html

from .models import Post, Category, Subscriber, UnsubscribeToken


# ===== Shared Utility =====
def generate_unique_slug(instance, title):
    """Generate a unique slug for a given model instance."""
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    Model = instance.__class__
    while Model.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


def regenerate_slugs(modeladmin, request, queryset):
    """Admin bulk action to regenerate slugs."""
    updated = 0
    for obj in queryset:
        new_slug = generate_unique_slug(obj, obj.title)
        if obj.slug != new_slug:
            obj.slug = new_slug
            obj.save(update_fields=["slug"])
            updated += 1
    messages.success(request, f"{updated} slug(s) successfully regenerated.")


regenerate_slugs.short_description = "🔁 Regenerate selected slugs from titles"


# ===== Post Admin =====
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'created_at', 'regenerate_slug_link')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('title', 'content', 'excerpt')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    exclude = ('slug',)
    actions = [regenerate_slugs]

    # Custom link inside the list view
    def regenerate_slug_link(self, obj):
        return format_html(
            '<a class="button" href="{}">🔁 Regenerate</a>',
            f"regenerate-slug/{obj.pk}/"
        )
    regenerate_slug_link.short_description = "Regenerate Slug"
    regenerate_slug_link.allow_tags = True

    # Custom route for per-object regeneration
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "regenerate-slug/<int:object_id>/",
                self.admin_site.admin_view(self.regenerate_single_slug),
                name="post_regenerate_slug",
            ),
        ]
        return custom_urls + urls

    def regenerate_single_slug(self, request, object_id):
        obj = get_object_or_404(Post, pk=object_id)
        old_slug = obj.slug
        obj.slug = generate_unique_slug(obj, obj.title)
        obj.save(update_fields=["slug"])
        messages.success(
            request,
            f"Slug for '{obj.title}' regenerated "
            f"from '{old_slug}' → '{obj.slug}'."
        )
        return redirect(f"../../{object_id}/change/")


# ===== Category Admin =====
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'regenerate_slug_link')
    search_fields = ('title', 'description')
    readonly_fields = ('slug',)
    ordering = ('title',)
    exclude = ('slug',)
    actions = [regenerate_slugs]

    def regenerate_slug_link(self, obj):
        return format_html(
            '<a class="button" href="{}">🔁 Regenerate</a>',
            f"regenerate-slug/{obj.pk}/"
        )
    regenerate_slug_link.short_description = "Regenerate Slug"
    regenerate_slug_link.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "regenerate-slug/<int:object_id>/",
                self.admin_site.admin_view(self.regenerate_single_slug),
                name="category_regenerate_slug",
            ),
        ]
        return custom_urls + urls

    def regenerate_single_slug(self, request, object_id):
        obj = get_object_or_404(Category, pk=object_id)
        old_slug = obj.slug
        obj.slug = generate_unique_slug(obj, obj.title)
        obj.save(update_fields=["slug"])
        messages.success(
            request,
            f"Slug for '{obj.title}' regenerated "
            f"from '{old_slug}' → '{obj.slug}'."
        )
        return redirect(f"../../{object_id}/change/")


# ===== Subscribers =====
@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_confirmed', 'token_created_at')
    list_filter = ('is_confirmed',)
    search_fields = ('email',)
    ordering = ('-token_created_at',)


# ===== Unsubscribed Tokens =====
@admin.register(UnsubscribeToken)
class UnsubscribeTokenAdmin(admin.ModelAdmin):
    list_display = ('email', 'token', 'created_at', 'unsubscribed')
    list_filter = ('unsubscribed',)
    search_fields = ('email',)
    ordering = ('-created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(unsubscribed=True)
