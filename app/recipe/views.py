"""
Views for the Recipe APIs
"""

# Viewsets >> A class which specify a variety of views
# > View > Functions for different request methods
# Methods  =  list   (List all the models we have)
#             create (Create a new model)
#             retrieve (Retrieve a model instance)
#             update (Update a model instance)
#             partial_update (Update one or more fields of a model instance)
#             destroy (Delete a model instance)

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes
)

from rest_framework import (
    viewsets,
    mixins,  # mixins > Things that you can mix in to a view to add additional functionality
    status
)

from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from core.models import Tag
from core.models import Ingredient




from recipe import serializers


# Decorator that extend auto-generated schema that is created by drf_spectacular.
@extend_schema_view(
    # Extend schema for the `list` endpoint.
    # i.e. we are adding below filters to the auto-generated schema for the `list` endpoint.
    list=extend_schema(
        parameters=[
            # These are parameters that can be passed to requests that are made to list-API for this view.
            OpenApiParameter(
                # Specifying details of parameters that can be accepted in API request.
                'tags',
                OpenApiTypes.STR, # Type is a string (i.e. Comma Separated List)
                description='Comma separated list of tag IDs to filter',  # User-defined Description
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredient IDs to filter',
            )
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    # Model View Set >> Specifically setup to work directly with a django Model
    # We can use a lot of Existing logic provided by Model Serializer to perform CRUD operations
    """View for manage recipe APIs."""
    # ^ The above doc-string is automatically shown by Swagger-UI as API Details.


    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()  # Objects that are available to this view.
    # ^Specify which model to use

    authentication_classes = [TokenAuthentication]
    # ^In order to use any endpoint provided by this view, use Token Authentication

    permission_classes = [IsAuthenticated]
    # ^You have to be authenticated in order to use any endpoint provided by this view.


    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        # "1,2,3" >> [1,2,3]
        return [int(str_id) for str_id in qs.split(',')]


    # Overwriding default get_query_set() method
    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        tags = self.request.query_params.get('tags')  # Comma Separated list that is provided as string
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset  # So we can apply filters to queryset as we go

        if tags:  # if tags are provided
            tag_ids = self._params_to_ints(tags)
            
            # Filtering Syntax
            queryset = queryset.filter(tags__id__in=tag_ids)  # < How to filter on related on a Database table using Django.
            # ^Filter the `queryset` based on the `tags` that are provided.

        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)
            # ^Filter the `queryset` based on the `ingredients` that are provided.

        return queryset.filter(user=self.request.user).order_by('-id').distinct()
        # distinct() > to avoid duplicate results if multiple recipes assinged to same tags/ingredients
    
        # Only return recipes that belong to the authenticated user. (NOT All of the recipes)
        # We are filtering the `queryset` (i.e. all recipes returned above) based on the `user` that is authenticated.
    

    def get_serializer_class(self):
        """Return the serializer class for request."""

        if self.action == 'list':
            return serializers.RecipeSerializer  # Do Not Contain `Description`
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer  # Contain `Image`
        
        # ^If the action is `list`, we want to return the `RecipeSerializer` class.
        # ^If the action is anything else, we want to return the `RecipeDetailSerializer` class.
        
        return self.serializer_class  # Contain `Description`
        # ^Return the `serializer_class` that is specified as a variable above
    

    # This Method is called when an Object is created using `viewsets.ModelViewSet`
    def perform_create(self, serializer):
        """Create a new recipe."""

        serializer.save(user=self.request.user)
        # ^Save the recipe that is created by XXX authenticated user.
        # ^We are passing the `user` that is authenticated to the `serializer` that is being used to create the recipe.

        # This ensure that new recipes created have the User ID Assigned.

    
    @action(methods=['POST'], detail=True, url_path='upload-image') # Added custom @action decorator 
    # It specify different HTTP methods supported by custom action.
    # In this case, we are only supporting POST requests.
    # detail=True >> Action is apply to detail portion of Model View.
    # ^ i.e. A specific recipe must be provided.
    # url_path='upload-image' >> Custom URL path for the custom action.
    def upload_image(self, request, pk=None):
        """Upload an image to Recipe"""

        recipe = self.get_object()  # Get the recipe that is being updated (using the Primary Key that is specified for the action)
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )
        # ^ This will return the `RecipeImageSerializer`

        if serializer.is_valid():
            serializer.save()  # This will save the image to the Database.
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        # ^If the serializer is valid, we want to save the data and return the response.

        # If the serializer is invalid, we want to return the errors and a 400 Bad Request status code.
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    

@extend_schema_view(
    list = extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned to recipes.',
            )
        ]
    )
)
# NOTE: Mixins to be defined BEFORE GenericViewSet
# This class is used to add additional functionality to tags/ingrediets viewset.
class BaseRecipeAttrViewSet(mixins.DestroyModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    # Generic View Set >> A class which specify a variety of views
    # > View > Functions for different request methods (for CRUD operations)
    # Mixins Base Class is used to add additional functionality to a viewset.
    # mixins.ListModelMixin  > allows to add the listing functionality for listing models
    # mixins.UpdateModelMixin > allows to add the update functionality for updating models
    # mixins.DestroyModelMixin > allows to add the delete functionality for deleting models

    """Base viewset for recipe attributes."""
    authentication_classes = [TokenAuthentication]
    # ^In order to use any endpoint provided by this view, use Token Authentication

    permission_classes = [IsAuthenticated]
    # ^You have to be authenticated in order to use any endpoint provided by this view.

    # Overwriding default get_query_set() method
    def get_queryset(self):
        """Filter queryset to authenticated user."""

        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0)) # 0 = default value to return if assigned_only value not provided.
        )

        queryset = self.queryset  

        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)  # ^Filter the `queryset` based on the `recipe` that is provided
            # ^ There is a recipe that is associated with this value i.e. tag/ingredient.

        return queryset.filter(
            user=self.request.user 
            ).order_by('-name').distinct()  
    
        # ^Only return tags that belong to the authenticated user. (NOT All of the tags)
        # We are filtering the `queryset` (i.e. all tags returned above) based on the `user` that is authenticated.
        # ^We are ordering the tags by their name in descending order.
        # ^This ensures that the tags are sorted in alphabetical order.
        # ^This is important because we want to display the tags in alphabetical order.


# Below classes Inherit from BaseRecipeAttrViewSet.
# All functions are defined in BaseRecipeAttrViewSet.

class TagViewSet(BaseRecipeAttrViewSet):

    """Manage tags in the database."""

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    # ^Specify which model to use


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database."""

    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
    # ^Specify which model to use

   

