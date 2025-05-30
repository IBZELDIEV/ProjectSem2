from django.urls import path
from .views import SignUpView, ProfileView, ProfileEditView, CustomPasswordChangeView, DeleteAccountView
from django.contrib.auth import views as auth_views 

app_name = 'accounts'

urlpatterns = [
    path('create/', SignUpView.as_view(), name='signup'),
    path('profile/', ProfileView.as_view(), name='user_profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='edit_profile'),
    path('change_password/', CustomPasswordChangeView.as_view(), name='change_password'),
    path('delete_account/', DeleteAccountView.as_view(), name='delete_account'),


    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'
    ), name='password_change_done'),
]
