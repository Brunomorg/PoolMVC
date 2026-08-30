from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import Thema, Person, Ausgabe


# 1. Startseite: Themen auflisten und neue erstellen
def themen_liste(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        # Thema erstellen
        if action == 'add_thema':
            titel = request.POST.get('titel', '').strip()
            if titel:
                Thema.objects.create(titel=titel)

        # Thema löschen (Löscht automatisch auch alle zugehörigen Ausgaben durch CASCADE)
        elif action == 'delete_thema':
            thema_id = request.POST.get('thema_id')
            if thema_id:
                Thema.objects.filter(id=thema_id).delete()

        return redirect('themen_liste')

    themen = Thema.objects.all().order_by('-erstellt_am')
    return render(request, 'pool/themen_liste.html', {'themen': themen})


# 2. Detailseite: Ausgaben verwalten
def thema_detail(request, thema_id):
    thema = get_object_or_404(Thema, id=thema_id)

    # --- FORMULAR-VERARBEITUNG (POST) ---
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_person':
            name = request.POST.get('person_name', '').strip()
            if name:
                Person.objects.get_or_create(thema=thema, name=name)
            return redirect('thema_detail', thema_id=thema.id)

        elif action == 'delete_person':
            person_id = request.POST.get('person_id')
            if person_id:
                Person.objects.filter(id=person_id, thema=thema).delete()
            return redirect('thema_detail', thema_id=thema.id)

        elif action == 'add_ausgabe':
            person_id = request.POST.get('person_id')
            betrag = request.POST.get('betrag')
            beschreibung = request.POST.get('beschreibung', '').strip()

            if person_id and betrag:
                person = Person.objects.get(id=person_id, thema=thema)
                Ausgabe.objects.create(
                    thema=thema,
                    person=person,
                    betrag=betrag,
                    beschreibung=beschreibung
                )
            return redirect('thema_detail', thema_id=thema.id)

        elif action == 'delete_ausgabe':
            ausgabe_id = request.POST.get('ausgabe_id')
            if ausgabe_id:
                Ausgabe.objects.filter(id=ausgabe_id, thema=thema).delete()
            return redirect('thema_detail', thema_id=thema.id)

    # --- ANZEIGE & BERECHNUNG (GET) ---
    personen = Person.objects.filter(thema=thema)
    ausgaben = Ausgabe.objects.filter(thema=thema).select_related('person')

    # 1. Gesamtausgaben sicher als float konvertieren
    summe = ausgaben.aggregate(Sum('betrag'))['betrag__sum']
    Gesamtsumme = float(summe) if summe is not None else 0.0

    # 2. Pro-Kopf-Betrag berechnen
    anzahl_personen = personen.count()
    pro_kopf = (Gesamtsumme / anzahl_personen) if anzahl_personen > 0 else 0.0

    # 3. Personen-Übersicht berechnen
    personen_übersicht = []
    for person in personen:
        p_summe = ausgaben.filter(person=person).aggregate(Sum('betrag'))['betrag__sum']

        # KORREKTUR: p_summe direkt in float umwandeln
        einzahlung = float(p_summe) if p_summe is not None else 0.0

        # Nun rechnen float - float (funktioniert ohne TypeError)
        saldo = einzahlung - pro_kopf

        personen_übersicht.append({
            'id': person.id,
            'name': person.name,
            'ausgegeben': einzahlung,
            'saldo': saldo
        })

    return render(request, 'pool/thema_detail.html', {
        'thema': thema,
        'personen': personen,
        'ausgaben': ausgaben,
        'gesamtausgaben': Gesamtsumme,
        'pro_kopf': pro_kopf,
        'personen_übersicht': personen_übersicht,
    })


def ausgabe_bearbeiten(request, ausgabe_id):
    ausgabe = get_object_or_404(Ausgabe, id=ausgabe_id)
    thema = ausgabe.thema  # <-- Das Thema aus der Ausgabe auslesen

    if request.method == 'POST':
        person_id = request.POST.get('person_id')
        betrag = request.POST.get('betrag')
        beschreibung = request.POST.get('beschreibung', '').strip()

        if person_id and betrag and beschreibung:
            ausgabe.person_id = person_id
            ausgabe.betrag = betrag
            ausgabe.beschreibung = beschreibung
            ausgabe.save()
            return redirect('thema_detail', thema_id=thema.id)

    personen = Person.objects.filter(thema=thema)

    # WICHTIG: 'thema' muss im Context-Dictionary enthalten sein!
    return render(request, 'pool/ausgabe_bearbeiten.html', {
        'ausgabe': ausgabe,
        'thema': thema,
        'personen': personen,
    })