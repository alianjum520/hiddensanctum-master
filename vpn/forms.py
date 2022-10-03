from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import NewsLetter, Contact

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
        })
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class NewsLetterForm(ModelForm):

    class Meta:
        model = NewsLetter
        fields = ['email']


class ContactForm(ModelForm):

    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']