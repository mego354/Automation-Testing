from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import APP
from django.utils.translation import gettext_lazy as _

ERROR_MESSAGES = {
    'required': _("This field is required."),
    'invalid': _("Enter a valid value."),
    'max_length': _("Ensure this value has at most {max_length} characters (it has {length})."),
    'min_length': _("Ensure this value has at least {min_length} characters (it has {length})."),
    'password_mismatch': _("The two password fields didn't match."),
}

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        error_messages={
            'required': ERROR_MESSAGES['required'],
            'invalid': ERROR_MESSAGES['invalid'],
        }
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        error_messages = {
            'username': {
                'required': ERROR_MESSAGES['required'],
                'max_length': ERROR_MESSAGES['max_length'],
            },
            'email': {
                'required': ERROR_MESSAGES['required'],
                'invalid': ERROR_MESSAGES['invalid'],
            },
            'password1': {
                'required': ERROR_MESSAGES['required'],
                'min_length': ERROR_MESSAGES['min_length'],
            },
            'password2': {
                'required': ERROR_MESSAGES['required'],
                'min_length': ERROR_MESSAGES['min_length'],
                'password_mismatch': ERROR_MESSAGES['password_mismatch'],  # Custom message for password mismatch
            },
        }       

class APPForm(forms.ModelForm):
    
    class Meta:
        model = APP
        fields = ['name', 'apk_file_path']
        labels = {
            'name': _("App name"),
            'apk_file_path': _("APK File Path"),
        }
        help_texts = {
            'name': _("Enter the name of the application."),
            'apk_file_path': _("Choose an APK."),
        }
        error_messages = {
            'name': {
                'required': ERROR_MESSAGES['required'],
                'max_length': ERROR_MESSAGES['max_length'],
            },
            'apk_file_path': {
                'required': ERROR_MESSAGES['required'],
            },
        }

    def clean_apk_file_path(self):
        apk_file = self.cleaned_data.get('apk_file_path')

        if apk_file:
            if not apk_file.name.endswith('.apk'):
                raise forms.ValidationError(_("The file must be an APK."))

        return apk_file