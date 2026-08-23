from django.db import models


class Thema(models.Model):
    titel = models.CharField(max_length=100)  # z. B. "Essen", "Trinken"
    erstellt_am = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titel

class Person(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Ausgabe(models.Model):
    thema = models.ForeignKey(Thema, on_delete=models.CASCADE, related_name='ausgaben')  # Neu!
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='ausgaben')
    betrag = models.DecimalField(max_digits=8, decimal_places=2)
    beschreibung = models.CharField(max_length=200)
    datum = models.DateTimeField(auto_now_add=True)  # Speichert automatisch das Erstellungsdatum

    def __str__(self):
        return f"{self.person.name}: {self.betrag} € für {self.beschreibung}"