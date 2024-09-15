from django.contrib import admin
from django.contrib.auth import get_user_model

from recipes.models import (
    Ingredient,
    Recipe,
    Subscription,
    Tag,
)


User = get_user_model()


class DisplayModelAdmin(admin.ModelAdmin):
    """Display all fields for any model."""

    def __init__(self, model, admin_site):
        """For the list display."""
        self.list_display = [
            field.name for field in model._meta.fields if field.name != 'id'
        ]
        super().__init__(model, admin_site)


@admin.register(Tag)
class TagAdmin(DisplayModelAdmin):
    """Admin tags."""


@admin.register(Ingredient)
class IngredientAdmin(DisplayModelAdmin):
    """Admin ingredients."""


@admin.register(Recipe)
class RecipeAdmin(DisplayModelAdmin):
    """Admin recipes."""


@admin.register(User)
class UserAdmin(DisplayModelAdmin):
    """Admin users."""


@admin.register(Subscription)
class SubscriptionAdmin(DisplayModelAdmin):
    """Admin subscriptions."""
