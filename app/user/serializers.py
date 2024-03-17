"""
Serializers for the User API View
"""

from django.contrib.auth import (
    get_user_model,
    authenticate,
)

from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _




class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    # Serialize is a way to convert object to and from python object
    # Serialization === JSON Object > Validation > Python Object / Database Model

    # v Definition of our Model
    class Meta:
        model = get_user_model()  # Model which serializer is representing
        fields = ('email', 'password', 'name')  # Fields to be serialized what users can define (Min Info)
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}  # Providing metadata to different fields 
        # ^(kwargs) = Key-Word Arguments
        # ^(write_only) = Field is not returned as an API response

    def create(self, validated_data):
        """Create and return a new user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)
        # ^This method is only called after validation as defined in class Meta is successful

    # Overriding default 'update' method of `serializers.ModelSerializer`
    def update(self, instance, validated_data):
        """Update and return the user"""
        # instance = Model Instance that is being updated
        # validated_data = Data that is already passed through serlizer validation

        password = validated_data.pop('password', None)  # Retreive that password from validated_data and remove it from validated_data afterwards
        user = super().update(instance, validated_data)  # Call the default update method of `serializers.ModelSerializer`
        # ^This will update the user instance with the validated_data (except for the password)

        # Check if a password was provided and update the user's password if it was provided
        if password:
            user.set_password(password)
            user.save()

        return user  # Return the updated user instance (so it can be used by the View if required)
    

class AuthTokenSerializer(serializers.Serializer):
    # ^Default Serializer Class
    """Serializer for the user authentication object"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},  # To Hide Text when using The Browesable API
        trim_whitespace=False  # Consider Space as a Character
    )

    def validate(self, attrs):
        # ^Method called at validation stage by our view
        # Data Posted to View > Data Passed to Serializer > Call Validate Method 

        """Validate and authenticate the user"""
        email = attrs.get('email')  # Retreiving Email and Pass
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')  # Standard Way to raise error with Serializers
            # ^The view will translate it to HTTP 400 Bad Request
            # ^Above msg will be shown to the client
            # Breaks the code here

        attrs['user'] = user  # Set User Attributes if the Authentication is successful
        return attrs
        # ^Return the validated data
