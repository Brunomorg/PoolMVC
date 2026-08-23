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
                Person.objects.get_or_create(name=name)
            return redirect('thema_detail', thema_id=thema.id)

        elif action == 'add_ausgabe':
            person_id = request.POST.get('person_id')
            betrag = request.POST.get('betrag')
            beschreibung = request.POST.get('beschreibung', '').strip()

            if person_id and betrag:
                person = Person.objects.get(id=person_id)
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

    # --- BERECHNUNG & ANZEIGE (GET) ---
    ausgaben = Ausgabe.objects.filter(thema=thema).select_related('person')
    personen = Person.objects.all()

    gesamtsumme = ausgaben.aggregate(Sum('betrag'))['betrag__sum'] or 0
    anzahl_personen = personen.count()
    pro_kopf = gesamtsumme / anzahl_personen if anzahl_personen > 0 else 0

    # 1. Ausgaben pro Person berechnen
    personen_übersicht = []
    schuldner = []
    glaeubiger = []

    for person in personen:
        einzahlung = ausgaben.filter(person=person).aggregate(Sum('betrag'))['betrag__sum'] or 0
        saldo = float(einzahlung - pro_kopf)

        personen_übersicht.append({
            'name': person.name,
            'ausgegeben': einzahlung,
            'saldo': saldo
        })

        if saldo < -0.01:
            schuldner.append({'person': person, 'betrag': abs(saldo)})
        elif saldo > 0.01:
            glaeubiger.append({'person': person, 'betrag': saldo})

    # 2. Schulden-Verrechnung (Wer zahlt an wen)
    ausgleich_liste = []
    i, j = 0, 0
    while i < len(schuldner) and j < len(glaeubiger):
        s = schuldner[i]
        g = glaeubiger[j]
        zahlungs_betrag = min(s['betrag'], g['betrag'])

        ausgleich_liste.append({
            'von': s['person'].name,
            'an': g['person'].name,
            'betrag': round(zahlungs_betrag, 2)
        })

        s['betrag'] -= zahlungs_betrag
        g['betrag'] -= zahlungs_betrag
        if s['betrag'] < 0.01: i += 1
        if g['betrag'] < 0.01: j += 1

    context = {
        'thema': thema,
        'personen': personen,
        'ausgaben': ausgaben,
        'gesamtsumme': gesamtsumme,
        'pro_kopf': round(pro_kopf, 2),
        'personen_übersicht': personen_übersicht,
        'ausgleich_liste': ausgleich_liste,
    }
    return render(request, 'pool/thema_detail.html', context)


def ausgabe_bearbeiten(request, ausgabe_id):
    ausgabe = get_object_or_404(Ausgabe, id=ausgabe_id)

    if request.method == 'POST':
        person_id = request.POST.get('person_id')
        betrag = request.POST.get('betrag')
        beschreibung = request.POST.get('beschreibung', '').strip()

        if person_id and betrag:
            ausgabe.person = Person.objects.get(id=person_id)
            ausgabe.betrag = betrag
            ausgabe.beschreibung = beschreibung
            ausgabe.save()  # Aktualisiert den bestehenden Eintrag in der Datenbank

            # Leitet zurück zur Detailansicht des jeweiligen Themas
            return redirect('thema_detail', thema_id=ausgabe.thema.id)

    personen = Person.objects.all()
    context = {
        'ausgabe': ausgabe,
        'personen': personen,
    }
    return render(request, 'pool/ausgabe_bearbeiten.html', context)