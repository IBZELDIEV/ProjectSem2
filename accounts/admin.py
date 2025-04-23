from django.contrib import admin
from .models import CustomUser, Profile
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display=['email','username','age']
    fieldsets= UserAdmin.fieldsets + ((None,{"fields":("age",)}),)
    add_fieldsets = (
        (
            None,
            {
                "classes":("wide",),
                "fields":("username","email","age","password1","password2"),
            },
        ),
    )

# Register your models here.
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile)
