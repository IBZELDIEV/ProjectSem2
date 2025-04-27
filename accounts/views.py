from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import DetailView
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Profile
from django.views import View

# --- Sign Up ---
class SignUpView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('shop:all_products')

    def form_valid(self, form):
        response = super().form_valid(form)
        customer_group, created = Group.objects.get_or_create(name='Customer')
        self.object.groups.add(customer_group)
        login(self.request, self.object)
        return response

# --- User Profile ---
class ProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'registration/user_profile.html'
    context_object_name = 'user'

    def get_object(self):
        return self.request.user

# --- Edit Profile ---
class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'registration/edit_profile.html'
    success_url = reverse_lazy('accounts:user_profile')

    def get_object(self):
        return self.request.user

# --- Change Password ---
class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'registration/change_password.html'
    success_url = reverse_lazy('accounts:password_change_done')

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)  # Important!
        return super().form_valid(form)



class DeleteAccountView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        logout(request)
        user.delete()
        return redirect('shop:all_products')