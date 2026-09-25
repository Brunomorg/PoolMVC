from django import forms
from .models import Topic, Person, Expense

# Form to create a new topic.
class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['titel']
        widgets = {
            'titel': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Themenname (z. B. Urlaubsreise)'
            })
        }


ThemaForm = TopicForm


# Form to create a new Person associated with a topic.
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


# Form to create a new spending associated with a topic and person.
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
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

    # Filtering persons in the form
    def __init__(self, *args, **kwargs):
        topic = kwargs.pop('thema', None)
        super().__init__(*args, **kwargs)
        if topic:
            self.fields['person'].queryset = Person.objects.filter(thema=topic)
            self.fields['person'].empty_label = "-- Person auswählen --"


AusgabeForm = ExpenseForm