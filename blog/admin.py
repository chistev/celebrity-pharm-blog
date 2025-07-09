from django.contrib import admin
from .models import Post, Category, Subscriber, UnsubscribeToken

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at')
    prepopulated_fields = {'slug': ('title',)}  # Automatically fill slug from title
    search_fields = ('title', 'content')
    list_filter = ('category', 'created_at')
    readonly_fields = ('created_at',)  # Optional: Show but prevent editing

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'description')

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_confirmed', 'token_created_at')
    list_filter = ('is_confirmed',)
    search_fields = ('email',)

@admin.register(UnsubscribeToken)
class UnsubscribeTokenAdmin(admin.ModelAdmin):
    list_display = ('email', 'token', 'created_at', 'unsubscribed')
    list_filter = ('unsubscribed',)
    search_fields = ('email',)
    
    def get_queryset(self, request):
        # Only show unsubscribed users
        qs = super().get_queryset(request)
        return qs.filter(unsubscribed=True)