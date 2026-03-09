from datetime import date, timedelta
import pytest
from pytest_bdd import scenarios, given, when, then, parsers

from core.expense_service import ExpenseService
from core.in_memory_expense_repository import InMemoryExpenseRepository
from core.domain_error import InvalidAmountError, InvalidExpenseDateError

scenarios("./expense_management.feature")


@pytest.fixture
def context():
    repo = InMemoryExpenseRepository()
    service = ExpenseService(repo)
    return {"service": service, "db": repo}


@given(parsers.parse("un gestor de gastos vacío"))
def empty_manager(context):
    pass


@given(parsers.parse("un gestor con un gasto de {amount:d} euros"))
def manager_with_one_expense(context, amount):
    context["service"].create_expense(
        title="Gasto inicial", amount=amount, description="", expense_date=date.today()
    )


@when(parsers.parse("añado un gasto de {amount:d} euros llamado {title}"))
def add_expense(context, amount, title):
    context["service"].create_expense(
        title=title, amount=amount, description="", expense_date=date.today()
    )


@when(parsers.parse("elimino el gasto con id {expense_id:d}"))
def remove_expense(context, expense_id):
    context["service"].remove_expense(expense_id)


@then(parsers.parse("el total de dinero gastado debe ser {total:d} euros"))
def check_total(context, total):
    assert context["service"].total_amount() == total


@then(parsers.parse("{month_name} debe sumar {expected_total:d} euros"))
def check_month_total(context, month_name, expected_total):
    total_actual = context["totals"].get(month_name, 0)
    assert total_actual == expected_total


@then(parsers.parse("debe haber {expenses:d} gastos registrados"))
def check_expenses_length(context, expenses):
    total = len(context["db"]._expenses)
    assert expenses == total


@then(parsers.parse("el titulo del gasto {expense_id:d} debe ser {expected_title}"))
def check_expense_title(context, expense_id, expected_title):
    expenses = context["service"].list_expenses()
    expense = next((e for e in expenses if e.id == expense_id), None)
    
    assert expense is not None
    assert expense.title == expected_title

@when(parsers.parse("intento añadir un gasto inválido de {amount:d} euros llamado {title}"))
def try_add_invalid_amount(context, amount, title):
    try:
        context["service"].create_expense(title=title, amount=amount)
    except InvalidAmountError:
        pass

@when(parsers.parse("intento añadir un gasto de {amount:d} euros llamado {title} para mañana"))
def try_add_future_expense(context, amount, title):
    tomorrow = date.today() + timedelta(days=1)
    try:
        context["service"].create_expense(title=title, amount=amount, expense_date=tomorrow)
    except InvalidExpenseDateError:
        pass