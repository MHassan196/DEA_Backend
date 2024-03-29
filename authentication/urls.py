from django.urls import path
from .views import change_password, forgot_password, register_user, user_login, user_logout, get_user_profile, update_user_profile


urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', user_login, name='login'),  
    path('logout/', user_logout, name='logout'),
    path('get_user_profile/', get_user_profile, name='get_user_profile'),  # Add this line for fetching user profile
    path('update_user_profile/<int:id>/', update_user_profile, name='update_user_profile'),
    path('change_password/', change_password, name='change_password'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    

    # path('change_password/', change_password, name='change_password'),
]