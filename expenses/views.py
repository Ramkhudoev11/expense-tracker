import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.db.models import Sum
from .models import Expense
from .forms import ExpenseForm, RegisterForm


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
        'date_from': date_from or '',
        'date_to': date_to or '',
    }
    return render(request, 'expenses/expense_list.html', context)


@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'expenses/expense_form.html', {'form': form, 'is_edit': False})


@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/expense_form.html', {'form': form, 'is_edit': True})


@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        return redirect('expense_list')
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})


@login_required
def stats(request):
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
            login(request, user)
            return redirect('expense_list')
    else:
        form = RegisterForm()
    return render(request, 'expenses/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('expense_list')