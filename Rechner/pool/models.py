from django.db import models

# Database entry for topics
class Thema(models.Model):
    titel = models.CharField(max_length=200)
    erstellt_am = models.DateTimeField(auto_now_add=True)

    # Show the name in the admin and lists
    def __str__(self):
        return self.titel

# Database entry for a person
class Person(models.Model):
    thema = models.ForeignKey(Thema, on_delete=models.CASCADE, related_name='personen')
    name = models.CharField(max_length=100)

    # Show the person's name
    def __str__(self):
        return self.name

    def gesamt_ausgaben(self):
        summe = self.ausgaben.filter(thema=self.thema).aggregate(Sum('betrag'))['betrag__sum']
        return float(summe) if summe is not None else 0.0

    def berechne_saldo(self, pro_kopf):
        return self.gesamt_ausgaben() - pro_kopf

# Database entry for expenses
class Ausgabe(models.Model):
    thema = models.ForeignKey(Thema, on_delete=models.CASCADE, related_name='ausgaben')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='ausgaben')
    betrag = models.DecimalField(max_digits=10, decimal_places=2)
    beschreibung = models.CharField(max_length=255)
    erstellt_am = models.DateTimeField(auto_now_add=True)  # Automatically stores the creation date

    # Show the description of the expense
    def __str__(self):
        return f"{self.person.name}: {self.betrag} € für {self.beschreibung}"