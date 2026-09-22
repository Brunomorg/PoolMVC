from django import forms
from .models import Thema, Person, Ausgabe

# Form to create a new Thema (topic).
class ThemaForm(forms.ModelForm):
    class Meta:
        model = Thema
        fields = ['titel']
        widgets = {
            'titel': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Themenname (z. B. Urlaubsreise)'
            })
        }

# Form to create a new Person associated with a Thema.
class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name der Person'
            })
        }

# Form to create a new Spending associated with a Thema and Person.
class AusgabeForm(forms.ModelForm):
    class Meta:
        model = Ausgabe
        fields = ['person', 'betrag', 'beschreibung']
        widgets = {
            'person': forms.Select(attrs={'class': 'form-control'}),
            'betrag': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'beschreibung': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'z. B. Einkaufen'
            }),
        }

    # Filtering Persons in the form
    def __init__(self, *args, **kwargs):
        thema = kwargs.pop('thema', None)
        super().__init__(*args, **kwargs)
        if thema:
            self.fields['person'].queryset = Person.objects.filter(thema=thema)
            self.fields['person'].empty_label = "-- Person auswählen --"