from django.db import models

#Database entry for Topics
class Thema(models.Model):
    titel = models.CharField(max_length=200)
    erstellt_am = models.DateTimeField(auto_now_add=True)

    # Show Name in Admin and Lists
    def __str__(self):
        return self.titel
    
# Database entry for Person
class Person(models.Model):
    thema = models.ForeignKey(Thema, on_delete=models.CASCADE, related_name='personen')
    name = models.CharField(max_length=100)

    # Show Name of the Person.
    def __str__(self):
        return self.name
    
# Database entry for Spendings
class Ausgabe(models.Model):
    thema = models.ForeignKey(Thema, on_delete=models.CASCADE, related_name='ausgaben')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='ausgaben')
    betrag = models.DecimalField(max_digits=10, decimal_places=2)
    beschreibung = models.CharField(max_length=255)
    erstellt_am = models.DateTimeField(auto_now_add=True)  # Speichert automatisch das Erstellungsdatum

    # Show Description of the Spending.
    def __str__(self):
        return f"{self.person.name}: {self.betrag} € für {self.beschreibung}"