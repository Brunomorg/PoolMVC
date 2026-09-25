from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from .models import Topic, Person, Expense
from .forms import TopicForm, PersonForm, ExpenseForm


# Topic Displaying and creating new Topics
def topic_list(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete_topic':
            topic_id = request.POST.get('topic_id')
            if topic_id:
                Topic.objects.filter(id=topic_id).delete()
            return redirect('topics_list')

        form = TopicForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('topics_list')
    else:
        form = TopicForm()

    topics = Topic.objects.all().order_by('-erstellt_am')
    return render(request, 'pool/themen_liste.html', {
        'themen': topics,
        'topics': topics,
        'form': form,
    })


themen_liste = topic_list


# Show Details of a Topic
def topic_detail(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)

    # --- Forms logic (POST) ---
    if request.method == 'POST':
        action = request.POST.get('action')

        match action:
            case 'add_person':
                person_form = PersonForm(request.POST)
                if person_form.is_valid():
                    person = person_form.save(commit=False)
                    person.thema = topic
                    person.save()

            case 'add_expense':
                expense_form = ExpenseForm(request.POST, thema=topic)
                if expense_form.is_valid():
                    expense = expense_form.save(commit=False)
                    expense.thema = topic
                    expense.save()

            case 'delete_person':
                person_id = request.POST.get('person_id')
                if person_id:
                    Person.objects.filter(id=person_id, thema=topic).delete()

            case 'delete_expense':
                expense_id = request.POST.get('ausgabe_id')
                if expense_id:
                    Expense.objects.filter(id=expense_id, thema=topic).delete()

        return redirect('topic_detail', topic_id=topic.id)

    # --- Initialize Browser Interface (GET) ---
    person_form = PersonForm()
    expense_form = ExpenseForm(thema=topic)

    people = Person.objects.filter(thema=topic)
    expenses = Expense.objects.filter(thema=topic).select_related('person')

    total_expenses_amount = expenses.aggregate(Sum('betrag'))['betrag__sum']
    total_expenses = float(total_expenses_amount) if total_expenses_amount is not None else 0.0

    person_count = people.count()
    per_person_share = (total_expenses / person_count) if person_count > 0 else 0.0

    people_summary = []
    for person in people:
        person_expense_total = expenses.filter(person=person).aggregate(Sum('betrag'))['betrag__sum']
        spent_amount = float(person_expense_total) if person_expense_total is not None else 0.0
        balance = spent_amount - per_person_share

        people_summary.append({
            'id': person.id,
            'name': person.name,
            'ausgegeben': spent_amount,
            'spent_amount': spent_amount,
            'saldo': balance,
            'balance': balance,
            'amount_due': abs(balance),
        })

    settlement_list = []
    debtors = [item for item in people_summary if item['balance'] < -0.01]
    creditors = [item for item in people_summary if item['balance'] > 0.01]
    debtors.sort(key=lambda item: item['balance'])
    creditors.sort(key=lambda item: item['balance'], reverse=True)

    while debtors and creditors:
        debtor = debtors[0]
        creditor = creditors[0]
        amount = min(abs(debtor['balance']), creditor['balance'])

        if amount <= 0.01:
            break

        settlement_list.append({
            'von': debtor['name'],
            'an': creditor['name'],
            'betrag': round(amount, 2),
            'amount': round(amount, 2),
        })

        debtor['balance'] = round(debtor['balance'] + amount, 2)
        creditor['balance'] = round(creditor['balance'] - amount, 2)

        if debtor['balance'] >= -0.01:
            debtors.pop(0)
        else:
            debtors[0] = debtor
            debtors.sort(key=lambda item: item['balance'])

        if creditor['balance'] <= 0.01:
            creditors.pop(0)
        else:
            creditors[0] = creditor
            creditors.sort(key=lambda item: item['balance'], reverse=True)

    return render(request, 'pool/thema_detail.html', {
        'thema': topic,
        'topic': topic,
        'personen': people,
        'people': people,
        'ausgaben': expenses,
        'expenses': expenses,
        'gesamtausgaben': total_expenses,
        'total_expenses': total_expenses,
        'per_person_share': per_person_share,
        'per_person_share': per_person_share,
        'personen_übersicht': people_summary,
        'people_summary': people_summary,
        'ausgleich_liste': settlement_list,
        'settlement_list': settlement_list,
        'person_form': person_form,
        'ausgabe_form': expense_form,
        'expense_form': expense_form,
    })


thema_detail = topic_detail


# Change existing Spending
def expense_edit(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    topic = expense.thema

    if request.method == 'POST':
        # Create Instance for updating already existing value
        form = ExpenseForm(request.POST, instance=expense, thema=topic)
        if form.is_valid():
            form.save()
            return redirect('topic_detail', topic_id=topic.id)
    else:
        form = ExpenseForm(instance=expense, thema=topic)

    return render(request, 'pool/ausgabe_bearbeiten.html', {
        'form': form,
        'ausgabe': expense,
        'expense': expense,
        'thema': topic,
        'topic': topic,
    })


ausgabe_bearbeiten = expense_edit