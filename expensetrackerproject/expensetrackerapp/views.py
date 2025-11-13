from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, login,logout
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from .models import ExpenseEntry, Login,Salary
from django.contrib import messages
import calendar
from datetime import datetime, timedelta
from django.templatetags.static import static
from django.template.loader import render_to_string
from .models import EMIPlan, EMIPayment
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from xhtml2pdf import pisa # type: ignore
from io import BytesIO
import os
from django.conf import settings
from django.http import HttpResponse
from django.templatetags.static import static
from django.conf import settings
from django.shortcuts import render
from xhtml2pdf import pisa # type: ignore
from datetime import datetime
import os
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa # type: ignore
from django.templatetags.static import static
from datetime import datetime



def create_emi(request):
    if request.method == 'POST':
        title = request.POST.get('tittle')
        amount_per_month = request.POST.get('amountpermonth')
        months = int(request.POST.get('months'))
        bank = request.POST.get('bank')
        start_date = request.POST.get('start_date')  

        plan = EMIPlan.objects.create(
            title=title,
            amount_per_month=amount_per_month,
            months=months,
            bank=bank
        )

        # Convert string date to Python date
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

        # ✅ EMI payments from chosen start date
        for m in range(1, months + 1):
            due_date = start_date + timedelta(days=30 * (m - 1))
            EMIPayment.objects.create(plan=plan, month_number=m, due_date=due_date)

        return redirect('emi_status', plan_id=plan.id)

    return render(request, 'emi.html')


def emi_status(request, plan_id):
    plan = EMIPlan.objects.get(id=plan_id)
    payments = plan.payments.all().order_by('month_number')
    return render(request, 'emi_status.html', {'plan': plan, 'payments': payments})


def mark_paid(request, payment_id):
    payment = EMIPayment.objects.get(id=payment_id)
    payment.is_paid = True
    payment.save()
    return redirect('emi_status', plan_id=payment.plan.id)

def emi_list(request):
    plans = EMIPlan.objects.all().order_by('-id')
    return render(request, 'emi_list.html', {'plans': plans})

def emi_status(request, plan_id):
    plan = EMIPlan.objects.get(id=plan_id)
    payments = plan.payments.all().order_by('month_number')
    return render(request, 'emi_status.html', {'plan': plan, 'payments': payments})

# DELETE EMI PLAN
def delete_emi(request, plan_id):
    plan = get_object_or_404(EMIPlan, id=plan_id)
    plan.delete()
    return redirect('emi_list')

def index(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # ✅ Correct function
            if user.is_superuser:
                return redirect('homepage2')  # admin homepage
            else:
                return redirect('homepage2')  # normal user homepage
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'login.html')
    return render(request, 'login.html')
def addexpense(request):
    if request.method == 'POST':
        date = request.POST.get('Date')
        category = request.POST.get('Category')
        description = request.POST.get('Description')
        income = float(request.POST.get('income') or 0)
        income_source = request.POST.get('income_source') or ""
        expense = float(request.POST.get('Expense') or 0)
        expense_source = request.POST.get('expense_source') or ""

        # ✅ Automatically calculate balance
        balance = income - expense

        # ✅ Get uploaded PDF file (if any)
        bill_pdf = request.FILES.get('bill_pdf')

        expense_entry = ExpenseEntry(
            date=date,
            category=category,
            description=description,
            income=income,
            income_source=income_source,
            expense=expense,
            expense_source=expense_source,
            balance=balance,  # ✅ Auto balance
            bill_pdf=bill_pdf  # ✅ Save uploaded PDF
        )
        expense_entry.save()

        return render(request, 'homepage.html', {'message': 'Data saved successfully!'})

    return render(request, 'homepage.html')


@login_required(login_url='login')
def viewexpenses(request):
    data = ExpenseEntry.objects.all()
    return render(request, 'detaails.html', {'data': data})


def update_expense(request, id):
    entry = get_object_or_404(ExpenseEntry, id=id)

    if request.method == 'POST':
        entry.date = request.POST.get('Date')
        entry.category = request.POST.get('Category')
        entry.description = request.POST.get('Description')
        entry.income = float(request.POST.get('income') or 0)
        entry.income_source = request.POST.get('income_source') or ""
        entry.expense = float(request.POST.get('Expense') or 0)
        entry.expense_source = request.POST.get('expense_source') or ""

        # ✅ Automatically recalculate balance
        entry.balance = entry.income - entry.expense

        entry.save()
        return redirect('homepage2')

    return render(request, 'update.html', {'entry': entry})


def deleteentry(request, id):
    expense = get_object_or_404(ExpenseEntry, id=id)

    if request.method == "POST":
        expense.delete()
        return redirect('homepage2')

    return render(request, 'deleteview.html', {'expense': expense})


def homepage2(request):
    now = datetime.now()
    current_year = now.year
    current_month = now.month

    # Read selected year & month from GET params (fallback to current)
    selected_year = int(request.GET.get('year', current_year))
    selected_month = int(request.GET.get('month', current_month))

    # Year range (for dropdown)
    years = list(range(2025, current_year + 2))

    # Month list (for buttons)
    months = [(calendar.month_name[i], i) for i in range(1, 13)]

    # Filter expenses by selected month and year
    expenses = ExpenseEntry.objects.filter(
        date__year=selected_year,
        date__month=selected_month
    ).order_by('date')

    # --- Monthly Totals ---
    total_income = sum(e.income for e in expenses)
    total_expense = sum(e.expense for e in expenses)
    total_balance = total_income - total_expense  # ✅ Auto computed

    # --- Grouped totals by source ---
    income_qs = (
        expenses.values('income_source')
        .annotate(total=Sum('income'))
        .order_by('income_source')
    )
    expense_qs = (
        expenses.values('expense_source')
        .annotate(total=Sum('expense'))
        .order_by('expense_source')
    )

    # ✅ Convert QuerySet to list of dicts (JSON serializable)
    income_by_source = list(income_qs)
    expense_by_source = list(expense_qs)

    month_name = calendar.month_name[selected_month]

    context = {
        'expenses': expenses,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'month_name': month_name,
        'months': months,
        'years': years,
        'total_income': total_income,
        'total_expense': total_expense,
        'total_balance': total_balance,
        'income_by_source': income_by_source,
        'expense_by_source': expense_by_source,
    }

    return render(request, 'homepage2.html', context)
def billview(request):
    
    return render(request, 'bill.html')

def invoice_page(request):
    return render(request, 'bill.html')

def get_next_bill_number():
    today = datetime.today().strftime("%Y%m%d") 
    counter_file = "bill_counter.txt"             

    if os.path.exists(counter_file):
        with open(counter_file, "r") as f:
            data = f.read().strip().split(",")
            last_date, last_number = data if len(data) == 2 else ("", "0")

            if last_date == today:
                new_number = int(last_number) + 1
            else:
                new_number = 1
    else:
        new_number = 1

    # Save current date and updated counter
    with open(counter_file, "w") as f:
        f.write(f"{today},{new_number}")

    # Final bill number format
    return f"BILL-{today}-{new_number:03d}"
@login_required(login_url='login')
def viewexpenses(request):
    data = ExpenseEntry.objects.all()
    return render(request, 'detaails.html', {'data': data})

def logout_view(request):
    logout(request)
    return redirect('index')  # or 'login' if you have a login view


def generate_pdf(request):
    if request.method == 'POST':
        items = request.POST.getlist('items[]')
        rates = request.POST.getlist('rates[]')
        qtys = request.POST.getlist('qtys[]')
        taxes = request.POST.getlist('taxes[]')

        item_list = []
        total_with_tax = 0
        has_tax = False  # ✅ Track if any tax is applied

        for i in range(len(items)):
            rate = float(rates[i])
            qty = float(qtys[i])
            tax_percent = float(taxes[i]) if i < len(taxes) else 0

            amount = rate * qty
            tax_amount = (amount * tax_percent) / 100
            total_item = amount + tax_amount
            total_with_tax += total_item

            if tax_percent > 0:
                has_tax = True

            item_list.append({
                'name': items[i],
                'rate': f"{rate:.2f}",
                'qty': qty,
                'amount': f"{amount:.2f}",
                'tax_percent': int(tax_percent),
                'tax_amount': f"{tax_amount:.2f}",
                'total_with_tax': f"{total_item:.2f}",
            })

        bill_number = get_next_bill_number()

        context = {
            'bill_number': bill_number,
            'invoice_date': datetime.today().strftime("%d-%m-%Y"),
            'customer_name': request.POST.get('customer_name', ''),
            'customer_address': request.POST.get('customer_address', ''),
            'items': item_list,
            'total_amount_with_tax': f"{total_with_tax:.2f}",
            'logo_path': request.build_absolute_uri(static('images/logo.png')),
            'signature_path': request.build_absolute_uri(static('images/signature.png')),
            'has_tax': has_tax,  # ✅ Pass flag to template
        }

        html = render_to_string('bill_pdf.html', context)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{bill_number}.pdf"'

        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error generating PDF <pre>' + html + '</pre>')
        return response
def firsthomepage(request):
        return render(request, 'firsthomepage.html')

def addsalary(request):
    if request.method == 'POST':
        employee_name = request.POST.get('employee_name')
        position = request.POST.get('position')
        basic_salary = request.POST.get('basic_salary')
        month = request.POST.get('month')

        Salary.objects.create(
            employee_name=employee_name,
            position=position,
            basic_salary=basic_salary,
            month=month,
            status='Paid' 
        )

        messages.success(request, 'Salary added successfully!')
        return redirect('salary_status')

    return render(request, 'managesalary.html')

def salary_status(request):
    salaries = Salary.objects.all().order_by('-id')
    return render(request, 'salarystatus.html', {'salaries': salaries})



