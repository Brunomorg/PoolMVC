from django.shortcuts import render, redirect
from django.db.models import Sum
from .models import Person, Ausgabe


def pool_uebersicht(request):
    # --- FORMULAR-VERARBEITUNG (POST) ---
    if request.method == 'POST':
        action = request.POST.get('action')

        # 1. Add person
        if action == 'add_person':
            name = request.POST.get('person_name', '').strip()
            if name:
                Person.objects.get_or_create(name=name)
            return redirect('pool_uebersicht')

        # 2. Add to pool
        elif action == 'add_ausgabe':
            person_id = request.POST.get('person_id')
            betrag = request.POST.get('betrag')
            beschreibung = request.POST.get('beschreibung', '').strip()

            if person_id and betrag:
                person = Person.objects.get(id=person_id)
                Ausgabe.objects.create(
                    person=person,
                    betrag=betrag,
                    beschreibung=beschreibung
                )
            return redirect('pool_uebersicht')

    # --- Calculate (GET) ---
    personen = Person.objects.all()
    ausgaben = Ausgabe.objects.select_related('person').all()

    gesamtsumme = ausgaben.aggregate(Sum('betrag'))['betrag__sum'] or 0
    anzahl_personen = personen.count()
    pro_kopf = gesamtsumme / anzahl_personen if anzahl_personen > 0 else 0

    schuldner = []
    glaeubiger = []

    for person in personen:
        einzahlung = ausgaben.filter(person=person).aggregate(Sum('betrag'))['betrag__sum'] or 0
        saldo = float(einzahlung - pro_kopf)

        if saldo < -0.01:
            schuldner.append({'person': person, 'betrag': abs(saldo)})
        elif saldo > 0.01:
            glaeubiger.append({'person': person, 'betrag': saldo})

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
        'personen': personen,
        'ausgaben': ausgaben,
        'gesamtsumme': gesamtsumme,
        'pro_kopf': round(pro_kopf, 2),
        'ausgleich_liste': ausgleich_liste,
    }
    return render(request, 'pool/index.html', context)