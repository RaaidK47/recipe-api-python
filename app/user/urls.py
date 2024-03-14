"""
URL Mappings for user API.
"""

from django.urls import path

from user import views


app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),  
    # ^ Definig Path
    # Converting Class Based View to supported Django View
    # name >> used for Reverse Lookup (as in test_user_api.py >> CREATE_USER_URL)

    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
]

# After creating URL, connect this to our Main APP >> (app/app/urls,py >> urlpatterns)