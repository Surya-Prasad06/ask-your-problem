from django import forms
from .models import Post, Profile, Comment, Message
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']  # Replace with your actual fields
# profile 
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']  # Include fields you want to update

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['username'].required = False  # Remove required
        self.fields['email'].required = False  # Remove required

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile  # Assuming Profile is the model for bio
        fields = ['bio', 'profile_picture']  # Include fields you want to update

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['bio'].required = False  # Remove required




class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(required=False, widget=forms.PasswordInput())
    new_password1 = forms.CharField(required=False, widget=forms.PasswordInput())
    new_password2 = forms.CharField(required=False, widget=forms.PasswordInput())



# comment form
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']  # Adjust the fields as per your Comment model

# message form
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type your message here...'})
        }