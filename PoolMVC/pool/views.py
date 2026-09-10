from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from .models import Thema, Person, Ausgabe
from .forms import ThemaForm, PersonForm, AusgabeForm

# Zeigt die Übersicht aller Themen an und verarbeitet das Anlegen eines neuen Themas.
def themen_liste(request):
    if request.method == 'POST':
        form = ThemaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('themen_liste')
    else:
        form = ThemaForm()

    themen = Thema.objects.all().order_by('-erstellt_am')
    return render(request, 'pool/themen_liste.html', {
        'themen': themen,
        'form': form
    })


# Zeigt die Details eines einzelnen Themas an und verarbeitet das Hinzufügen bzw. Entfernen von Personen und Ausgaben.
def thema_detail(request, thema_id):
    thema = get_object_or_404(Thema, id=thema_id)

    # --- Forms logic (POST) ---
    if request.method == 'POST':
        action = request.POST.get('action')

        match action:
            case 'add_person':
                person_form = PersonForm(request.POST)
                if person_form.is_valid():
                    person = person_form.save(commit=False)
                    person.thema = thema
                    person.save()

            case 'add_ausgabe':
                ausgabe_form = AusgabeForm(request.POST, thema=thema)
                if ausgabe_form.is_valid():
                    ausgabe = ausgabe_form.save(commit=False)
                    ausgabe.thema = thema
                    ausgabe.save()

            case 'delete_person':
                person_id = request.POST.get('person_id')
                if person_id:
                    Person.objects.filter(id=person_id, thema=thema).delete()

            case 'delete_ausgabe':
                ausgabe_id = request.POST.get('ausgabe_id')
                if ausgabe_id:
                    Ausgabe.objects.filter(id=ausgabe_id, thema=thema).delete()

        return redirect('thema_detail', thema_id=thema.id)

    # --- Initialize Browser Interface (GET) ---
    person_form = PersonForm()
    ausgabe_form = AusgabeForm(thema=thema)

    personen = Person.objects.filter(thema=thema)
    ausgaben = Ausgabe.objects.filter(thema=thema).select_related('person')

    summe = ausgaben.aggregate(Sum('betrag'))['betrag__sum']
    gesamtausgaben = float(summe) if summe is not None else 0.0

    anzahl_personen = personen.count()
    pro_kopf = (gesamtausgaben / anzahl_personen) if anzahl_personen > 0 else 0.0

    personen_übersicht = []
    for person in personen:
        p_summe = ausgaben.filter(person=person).aggregate(Sum('betrag'))['betrag__sum']
        einzahlung = float(p_summe) if p_summe is not None else 0.0
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
        'gesamtausgaben': gesamtausgaben,
        'pro_kopf': pro_kopf,
        'personen_übersicht': personen_übersicht,
        'person_form': person_form,
        'ausgabe_form': ausgabe_form,
    })


# Ermöglicht das Bearbeiten einer bestehenden Ausgabe und speichert die Änderungen wieder im Thema.
def ausgabe_bearbeiten(request, ausgabe_id):
    ausgabe = get_object_or_404(Ausgabe, id=ausgabe_id)
    thema = ausgabe.thema

    if request.method == 'POST':
        # Create Instance for updating already existing value
        form = AusgabeForm(request.POST, instance=ausgabe, thema=thema)
        if form.is_valid():
            form.save()
            return redirect('thema_detail', thema_id=thema.id)
    else:
        form = AusgabeForm(instance=ausgabe, thema=thema)

    return render(request, 'pool/ausgabe_bearbeiten.html', {
        'form': form,
        'ausgabe': ausgabe,
        'thema': thema,
    })