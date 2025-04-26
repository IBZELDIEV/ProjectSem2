from django.views.generic.edit import CreateView
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.urls import reverse
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.views.generic import CreateView, DetailView, UpdateView
from .models import CustomUser, Profile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import update_session_auth_hash


class SignUpView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('shop:all_products')
    def form_valid(self, form):
# Save the new user
        response = super().form_valid(form)
# Add user to the Customer group
        customer_group, created = Group.objects.get_or_create(name='Customer')
        self.object.groups.add(customer_group)
# Log the user in after signup

        login(self.request, self.object)
        return response # Redirect to success URL

class ProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'registration/user_profile.html'
    context_object_name = 'user'

    def get_object(self):
        return self.request.user

class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = CustomUser 
    form_class = CustomUserChangeForm
    template_name = 'registration/edit_profile.html'
    success_url = reverse_lazy('accounts:customer')

    def get_object(self):
        return self.request.user

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/change_password.html'
    success_url = reverse_lazy('accounts:password_change_done')

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)  # Important!
        return super().form_valid(form)

# views.py
