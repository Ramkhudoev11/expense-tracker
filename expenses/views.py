import hmac
import hashlib
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.db.models import Sum
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import Expense, Income, Subscription, ScheduleItem
from .forms import ExpenseForm, IncomeForm, RegisterForm, ScheduleItemForm


def expense_list(request):
    expenses = Expense.objects.filter(user=request.user) if request.user.is_authenticated else Expense.objects.none()

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if date_from:
        expenses = expenses.filter(date__gte=date_from)
    if date_to:
        expenses = expenses.filter(date__lte=date_to)

    total = sum(e.amount for e in expenses)
    context = {
        'expenses': expenses,
        'total': total,
        'total_json': json.dumps(float(total)),
        'date_from': date_from or '',
        'date_to': date_to or '',
    }
    return render(request, 'expenses/expense_list.html', context)


@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(user=request.user)
    return render(request, 'expenses/expense_form.html', {'form': form, 'is_edit': False, 'title': 'Добавить расход'})


@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense, user=request.user)
    return render(request, 'expenses/expense_form.html', {'form': form, 'is_edit': True, 'title': 'Редактировать расход'})


@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        return redirect('expense_list')
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})


def income_list(request):
    incomes = Income.objects.filter(user=request.user) if request.user.is_authenticated else Income.objects.none()

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if date_from:
        incomes = incomes.filter(date__gte=date_from)
    if date_to:
        incomes = incomes.filter(date__lte=date_to)

    total = sum(i.amount for i in incomes)
    context = {
        'incomes': incomes,
        'total': total,
        'total_json': json.dumps(float(total)),
        'date_from': date_from or '',
        'date_to': date_to or '',
    }
    return render(request, 'expenses/income_list.html', context)


@login_required
def add_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST, user=request.user)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            return redirect('income_list')
    else:
        form = IncomeForm(user=request.user)
    return render(request, 'expenses/income_form.html', {'form': form, 'is_edit': False, 'title': 'Добавить доход'})


@login_required
def edit_income(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('income_list')
    else:
        form = IncomeForm(instance=income, user=request.user)
        return render(request, 'expenses/income_form.html',
                      {'form': form, 'is_edit': True, 'title': 'Редактировать доход'})

@login_required
def delete_income(request, pk):
            income = get_object_or_404(Income, pk=pk, user=request.user)
            if request.method == 'POST':
                income.delete()
                return redirect('income_list')
            return render(request, 'expenses/income_confirm_delete.html', {'income': income})

@login_required
def schedule_list(request):
            items = ScheduleItem.objects.filter(user=request.user)
            return render(request, 'expenses/schedule_list.html', {'items': items})

@login_required
def add_schedule_item(request):
            if request.method == 'POST':
                form = ScheduleItemForm(request.POST)
                if form.is_valid():
                    item = form.save(commit=False)
                    item.user = request.user
                    item.save()
                    return redirect('schedule_list')
            else:
                form = ScheduleItemForm()
            return render(request, 'expenses/schedule_form.html', {'form': form, 'is_edit': False})

@login_required
def edit_schedule_item(request, pk):
            item = get_object_or_404(ScheduleItem, pk=pk, user=request.user)
            if request.method == 'POST':
                form = ScheduleItemForm(request.POST, instance=item)
                if form.is_valid():
                    form.save()
                    return redirect('schedule_list')
            else:
                form = ScheduleItemForm(instance=item)
            return render(request, 'expenses/schedule_form.html', {'form': form, 'is_edit': True})

@login_required
def delete_schedule_item(request, pk):
            item = get_object_or_404(ScheduleItem, pk=pk, user=request.user)
            if request.method == 'POST':
                item.delete()
                return redirect('schedule_list')
            return render(request, 'expenses/schedule_confirm_delete.html', {'item': item})

@login_required
def stats(request):
            subscription = getattr(request.user, 'subscription', None)
            if not subscription or not subscription.is_active:
                return redirect('pricing')

            category_totals = (
                Expense.objects
                .filter(user=request.user)
                .values('category__name')
                .annotate(total=Sum('amount'))
                .order_by('-total')
            )

            chart_labels = [item['category__name'] or 'Без категории' for item in category_totals]
            chart_values = [float(item['total']) for item in category_totals]

            context = {
                'category_totals': category_totals,
                'chart_labels': json.dumps(chart_labels),
                'chart_values': json.dumps(chart_values),
            }
            return render(request, 'expenses/stats.html', context)

def register(request):
            if request.method == 'POST':
                form = RegisterForm(request.POST)
                if form.is_valid():
                    user = form.save()
                    Subscription.objects.create(user=user)
                    login(request, user)
                    return redirect('expense_list')
            else:
                form = RegisterForm()
            return render(request, 'expenses/register.html', {'form': form})

def logout_view(request):
            logout(request)
            return redirect('expense_list')

@login_required
def pricing(request):
            subscription, _ = Subscription.objects.get_or_create(user=request.user)
            return render(request, 'expenses/pricing.html', {
                'subscription': subscription,
                'client_token': settings.PADDLE_CLIENT_TOKEN,
                'price_id': settings.PADDLE_PRICE_ID,
            })

@login_required
def checkout_success(request):
            return render(request, 'expenses/checkout_success.html')

def verify_paddle_signature(request):
            signature_header = request.META.get('HTTP_PADDLE_SIGNATURE', '')
            if not signature_header:
                return False
            parts = dict(item.split('=') for item in signature_header.split(';'))
            timestamp = parts.get('ts')
            signature = parts.get('h1')
            if not timestamp or not signature:
                return False
            signed_payload = f"{timestamp}:{request.body.decode('utf-8')}"
            computed = hmac.new(
                settings.PADDLE_WEBHOOK_SECRET.encode('utf-8'),
                signed_payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(computed, signature)


@csrf_exempt
def paddle_webhook(request):
    if not verify_paddle_signature(request):
        return HttpResponse(status=403)

    data = json.loads(request.body)
    event_type = data.get('event_type')
    event_data = data.get('data', {})

    if event_type == 'transaction.completed':
        custom_data = event_data.get('custom_data') or {}
        user_id = custom_data.get('user_id')
        customer_id = event_data.get('customer_id')
        subscription_id = event_data.get('subscription_id')
        if user_id:
            try:
                sub = Subscription.objects.get(user_id=user_id)
                sub.is_active = True
                sub.paddle_customer_id = customer_id
                sub.paddle_subscription_id = subscription_id
                sub.save()
            except Subscription.DoesNotExist:
                pass

    elif event_type in ('subscription.canceled', 'subscription.paused'):
        subscription_id = event_data.get('id')
        try:
            sub = Subscription.objects.get(paddle_subscription_id=subscription_id)
            sub.is_active = False
            sub.save()
        except Subscription.DoesNotExist:
            pass

    return HttpResponse(status=200)


def terms(request):
    return render(request, 'expenses/terms.html')


def privacy(request):
    return render(request, 'expenses/privacy.html')


def refund(request):
    return render(request, 'expenses/refund.html')