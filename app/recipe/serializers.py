"""
Serializer for recipe APIs
"""
# SERIALIZER >> Convert a Model Instance to a Python Data Type


from rest_framework import serializers

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)


# Defining TagSerializer above RecipeSerializer as it will be used as Nested Serializer
class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)

class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)

# This Serializer is going to represent a specific Model (i.e. Recipe Model)
class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe objects"""

    tags = TagSerializer(many=True, required=False)  # Tags are Optional 
    # ^ These nested serializer are by default read-only (you can't create)

    ingredients = IngredientSerializer(many=True, required=False)  # Ingredients are Optional

    class Meta:
        model = Recipe  # Tells DRF that we will use Recipe Model with this serializer
        fields = ('id', 'title', 'time_minutes', 'price', 'link' , 'tags', 'ingredients')
        read_only_fields = ('id',)  # We do not want to change Database ID of recipe.
        # Other filed can be changed/updated

    # Internal Methods start with a `_`
    # Internal Methods > Should not be called from outside the Class. (i.e. RecipeSerializer)
    def _get_or_create_tags(self, tags, recipe):
        """Handling getting or creating tags as needed"""

        auth_user = self.context.get('request').user  # ^Getting Authenticated User from context (request)
        # `context` is passed to serializer by the view 

        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag   # Pass all the fields associated with the tag (in case we add additional fileds to Tag in future)
            )  
            # ^Getting Tag Object if it exists in DB (or creating it if it doesn't exist)
            # This gives us functionality to not create duplicate tags in our system.

            recipe.tags.add(tag_obj)  # ^Adding Tag Object to Recipe Object 

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handling getting or creating ingredients as needed"""

        auth_user = self.context.get('request').user  # ^Getting Authenticated User from context (request)
        # `context` is passed to serializer by the view

        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient   
            )

            recipe.ingredients.add(ingredient_obj)  # ^Adding Ingredient Object to Recipe Object
        return recipe  # ^Returning Recipe Object with Ingredients added to it.
        

    # Overriding default 'create' method of `serializers.ModelSerializer` - To make them capable to make Recipe Objects with Tags
    def create(self, validated_data):
        """Create a Recipe"""
        tags = validated_data.pop('tags', [])  # ^Removing tags from validated_data  ( [] >  if not exists, default to an empty list )
        ingredients = validated_data.pop('ingredients', [])  # ^Removing ingredients from validated_data  ([] >  if not exists, default to an empty list)

        recipe = Recipe.objects.create(**validated_data)  # ^Creating Recipe Object (Without Tags)

        self._get_or_create_tags(tags, recipe)  # ^Adding Tags to Recipe Object  (Internal Function)

        self._get_or_create_ingredients(ingredients, recipe)  # ^Adding Ingredients to Recipe Object  (Internal Function)

        return recipe
    
    # Overriding default 'update' method of `serializers.ModelSerializer` - To make them capable to update Recipe Objects with Tags
    def update(self, instance, validated_data):
        """Update a Recipe"""

        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)

        if tags is not None:
            instance.tags.clear()  # ^Clearing Tags from Recipe Object
            self._get_or_create_tags(tags, instance)  # ^Adding Tags to Recipe Object  (Internal Function)

        if ingredients is not None:
            instance.ingredients.clear()  # ^Clearing Ingredients from Recipe Object
            self._get_or_create_ingredients(ingredients, instance)  # ^Adding Ingredients to Recipe Object  (Internal Function)

        # Everything else in validated_data (other than tags and ingredients) is going to be updated in the Recipe Object (i.e. title, time_minutes, price, link)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)  # ^Updating Attributes of Recipe Object

        instance.save()  # ^Saving Recipe Object  (instance = Recipe Object)
        return instance  # ^Returning Updated Recipe Object


class RecipeDetailSerializer(RecipeSerializer):
    """Serialize for recipe detail view"""
    # This class is Just Extenstion of RecipeSerializer

    class Meta(RecipeSerializer.Meta):
        # ^Getting all Meta Values provided to RecipeSerializer

        fields = RecipeSerializer.Meta.fields + ('description',)
        # ^Adding 'description' field to Meta Values provided to RecipeSerializer



    
