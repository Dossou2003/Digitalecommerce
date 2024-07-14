from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Commande, Contact, Paiement
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm


class ProductAddToCartForm(forms.Form):
    produit_nom= forms.CharField(label='Nom du produit', max_length=255)
    quantite=forms.IntegerField(label='quantite', min_value=1)
    

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'nom', 'prenom', 'telephone', 'role', 'password1', 'password2')

class InscriptionForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'nom', 'prenom', 'password1', 'password2']
        
class ConnexionForm(AuthenticationForm):
    class Meta:
        model = CustomUser  
        fields = ['username', 'password']

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['nom', 'email', 'message']

class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['commande', 'montant', 'type_paiement']



from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Cette adresse e-mail est déjà utilisée.')
        return email
