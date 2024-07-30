from django.conf import settings
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from user.models import User, Country, Currency, Language, UserProfile, UserVerification


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    filter_horizontal = ()
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    fieldsets = (
        ('Personal info', {'fields': (
            'email', 'password', 'user_type', 'first_name', 'last_name', 'verified')}),
        ('Permissions',
         {'fields': ('is_active', 'is_staff', 'is_superuser')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('password1', 'password2', 'first_name', 'last_name', 'is_active')}),
    )
    list_display = ['id', 'email', 'user_type', 'uuid',  'verified', 'is_active']
    search_fields = ('email',)
    ordering = ('email',)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'phone_code']


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['id', 'country_id', 'name']


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['id', 'country_id', 'name']


@admin.register(UserProfile)
class GizViewerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'picture', 'cover_picture', 'bio', 'gender', 'country', 'currency', 'language',
                    'city',
                    'twitter_link',
                    'linkedin_link', 'website_link',
                    'facebook_link', 'youtube_link']


@admin.register(UserVerification)
class UserVerificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'passport', 'profile_picture', 'header_image', 'bio', 'letter', 'status']