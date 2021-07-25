from django import forms
from django.db.models import fields
from django.forms.widgets import Widget
from .models import Account, UserProfile



class FormaRegistracion(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Entrar Contraseña',
    }))
    confirmar_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Confirmar Contraseña'
    }))

    class Meta:
        model  = Account
        fields = ['first_name','last_name','phone','email','password']



    def __init__(self, *args, **kwargs):
        super(FormaRegistracion, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder']='Entrar Nombre'
        self.fields['last_name'].widget.attrs['placeholder']='Entrar Apellido'
        self.fields['phone'].widget.attrs['placeholder']='Entrar Telefono'
        self.fields['email'].widget.attrs['placeholder']='Entrar Correo Electronico'   
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'


    def clean(self):
        cleaned_data = super(FormaRegistracion, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirmar_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "la Contraseña no es igual!!"
            )

class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name','last_name','phone')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'



class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages={'invalid':("Solo Imagen")}, widget = forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ('address_line_1','address_line_2','city', 'state','country','profile_picture')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'
