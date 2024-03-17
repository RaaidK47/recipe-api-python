"""
Serializer for recipe APIs
"""
# SERIALIZER >> Convert a Model Instance to a Python Data Type


from rest_framework import serializers

from core.models import Recipe

# This Serializer is going to represent a specific Model (i.e. Recipe Model)
class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe objects"""

    class Meta:
        model = Recipe  # Tells DRF that we will use Recipe Model with this serializer
        fields = ('id', 'title', 'time_minutes', 'price', 'link')
        read_only_fields = ('id',)  # We do not want to change Database ID of recipe.
        # Other filed can be changed/updated

class RecipeDetailSerializer(RecipeSerializer):
    """Serialize for recipe detail view"""
    # This class is Just Extenstion of RecipeSerializer

    class Meta(RecipeSerializer.Meta):
        # ^Getting all Meta Values provided to RecipeSerializer

        fields = RecipeSerializer.Meta.fields + ('description',)
        # ^Adding 'description' field to Meta Values provided to RecipeSerializer



    
