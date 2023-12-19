from django import forms
from .models import CustomUser, FacultyShift, Approval

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = CustomUser
        fields = ['user_picture', 'user_firstname', 'user_lastname', 'user_role', 'email', 'password']

        widgets = {
            'user_picture': forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'image/*'}),
            'user_firstname': forms.TextInput(attrs={'class': 'form-control'}),
            'user_lastname': forms.TextInput(attrs={'class': 'form-control'}),
            'user_role': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and not confirm_password:
            raise forms.ValidationError("Please confirm your password.")
        elif password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

class UserUpdateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = CustomUser
        fields = ['user_picture', 'user_firstname', 'user_lastname', 'user_role', 'email', 'password']

        widgets = {
            'user_picture': forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'image/*'}),
            'user_firstname': forms.TextInput(attrs={'class': 'form-control'}),
            'user_lastname': forms.TextInput(attrs={'class': 'form-control'}),
            'user_role': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and not confirm_password:
            raise forms.ValidationError("Please confirm your password.")
        elif password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('password')

        if new_password:
            user.set_password(new_password)

        if commit:
            user.save()

        return user
# class UserForm(forms.ModelForm):
#     class Meta:
#         model = CustomUser
#         fields = ['user_picture', 'user_firstname', 'user_lastname', 'user_role', 'email', 'password']

#     password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
#     confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)

#     def __init__(self, *args, **kwargs):
#         super(UserForm, self).__init__(*args, **kwargs)
#         for field in self.fields:
#             self.fields[field].widget.attrs['class'] = 'form-control'

#         self.fields['user_picture'].widget.attrs['class'] = 'form-control-file'
#         self.fields['user_picture'].widget.attrs['accept'] = 'image/*'

# class UserUpdateForm(UserForm):
#     class Meta(UserForm.Meta):
#         fields = ['user_picture', 'user_firstname', 'user_lastname', 'user_role', 'email']

#     def __init__(self, *args, **kwargs):
#         super(UserUpdateForm, self).__init__(*args, **kwargs)
#         self.fields['password'].required = False
#         self.fields['confirm_password'].required = False


class FacultyShiftForm(forms.ModelForm):
    class Meta:
        model = FacultyShift
        fields = ['shift_start', 'shift_end', 'shift_day']

        widgets = {
            'shift_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'shift_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'shift_day': forms.Select(attrs={'class': 'form-control'}),
        }

        labels = {
            'shift_start': 'Shift Start Time',
            'shift_end': 'Shift End Time',
            'shift_day': 'Shift Day',
        }

class ApprovalForm(forms.ModelForm):
    class Meta:
        model = Approval
        fields = ['decision', 'comment']
