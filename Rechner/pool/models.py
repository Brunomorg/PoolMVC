from django.db import models
from django.db.models import Sum

# Database entry for topics
class Topic(models.Model):
    titel = models.CharField(max_length=200)
    erstellt_am = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pool_thema'

    # Show the name in the admin and lists
    def __str__(self):
        return self.titel


Thema = Topic


# Database entry for a person
class Person(models.Model):
    thema = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='personen')
    name = models.CharField(max_length=100)

    # Show the person's name
    def __str__(self):
        return self.name

    def total_expenses(self):
        total = self.ausgaben.filter(thema=self.thema).aggregate(Sum('betrag'))['betrag__sum']
        return float(total) if total is not None else 0.0

    def calculate_balance(self, per_person_share):
        return round(self.total_expenses() - per_person_share, 2)

    def total_expenses(self):
        return self.total_expenses()

    def calculate_balance(self, per_person_share):
        return self.calculate_balance(per_person_share)


# Database entry for expenses
class Expense(models.Model):
    thema = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='ausgaben')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='ausgaben')
    betrag = models.DecimalField(max_digits=10, decimal_places=2)
    beschreibung = models.CharField(max_length=255)
    erstellt_am = models.DateTimeField(auto_now_add=True)  # Automatically stores the creation date

    class Meta:
        db_table = 'pool_ausgabe'

    # Show the description of the expense
    def __str__(self):
        return f"{self.person.name}: {self.betrag} € für {self.beschreibung}"


Ausgabe = Expense