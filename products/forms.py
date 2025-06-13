from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomUser, Address, Card

class CustomRegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None  # Remove the default help text

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street', 'city', 'state', 'postal_code', 'country']

class CardForm(forms.ModelForm):
    expiration_date = forms.DateField(
        input_formats=["%m/%Y"],
        widget=forms.TextInput(attrs={
            "placeholder": "MM/YYYY",
            "pattern": "(0[1-9]|1[0-2])/\\d{4}",
            "maxlength": "7",
        }),
        required=True,
    )

    class Meta:
        model = Card
        fields = ['card_number', 'cardholder_name', 'expiration_date', 'cvv']