from django.db import models


class Thema(models.Model):
    titel = models.CharField(max_length=200)
    erstellt_am = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titel

class Person(models.Model):
    # Jede Person gehört zu genau einem Thema
    thema = models.ForeignKey(Thema, on_delete=models.CASCADE, related_name='personen')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Ausgabe(models.Model):
    thema = models.ForeignKey(Thema, on_delete=models.CASCADE, related_name='ausgaben')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='ausgaben')
    betrag = models.DecimalField(max_digits=10, decimal_places=2)
    beschreibung = models.CharField(max_length=255)
    erstellt_am = models.DateTimeField(auto_now_add=True)  # Speichert automatisch das Erstellungsdatum

    def __str__(self):
        return f"{self.person.name}: {self.betrag} € für {self.beschreibung}"