from django import forms
from .models import Account


class RegistrationForm(forms.ModelForm):
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Ingrese Password',
        'class': 'form-control',
        
    }))
    
    confirm_passwords = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirmar Password',
        'class':'form-control',
    }))
    
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']
        
        
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args,**kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Ingrese Nombre'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Ingrese Apellido'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Ingrese Telefono'
        self.fields['email'].widget.attrs['placeholder'] = 'Ingrese Email'
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'
            
    
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_passwords')
        
        if password != confirm_password:
            raise forms.ValidationError('Password no coincide')