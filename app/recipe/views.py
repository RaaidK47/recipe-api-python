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

            

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe import serializers


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

    # Overwriding default get_query_set() method
    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id') 
    
        # Only return recipes that belong to the authenticated user. (NOT All of the recipes)
        # We are filtering the `queryset` (i.e. all recipes returned above) based on the `user` that is authenticated.
    

    def get_serializer_class(self):
        """Return the serializer class for request."""

        if self.action == 'list':
            return serializers.RecipeSerializer  # Do Not Contain `Description`
        
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
  




