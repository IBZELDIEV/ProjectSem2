from django.urls import path
from .views import SignUpView, ProfileView, ProfileEditView, CustomPasswordChangeView

app_name = 'accounts'

urlpatterns = [
    path('create/', SignUpView.as_view(), name='signup'),
    path('profile/', ProfileView.as_view(), name='user_profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='edit_profile'),
    path('change_password/', CustomPasswordChangeView.as_view(), name='change_password'),
    
]