from django.db import models

class ExpenseEntry(models.Model):
    date = models.DateField()
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    income = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    income_source = models.CharField(max_length=100, blank=True, null=True)
    expense_source = models.CharField(max_length=100, blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bill_pdf = models.FileField(upload_to='bills/', blank=True, null=True)

    def __str__(self):
        return f"{self.date} - {self.category} - Income: {self.income} Expense: {self.expense}"
class Login(models.Model):
    USER_TYPES = (
        ('user', 'User'),
        ('admin', 'Admin')
        )
    username=models.CharField(max_length=200)
    password=models.CharField(max_length=200)
    type=models.CharField(max_length=200,choices=USER_TYPES)
    def __str__(self):
        return self.username
    
class UserTable(models.Model):#for registration
    username=models.CharField(max_length=200)
    password=models.CharField(max_length=200)
    confirmpassword=models.CharField(max_length=200)
    def __str__(self):
        return self.username
from django.db import models

class EMIPlan(models.Model):
    title = models.CharField(max_length=100)
    amount_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    months = models.IntegerField()
    bank = models.CharField(max_length=100)
    start_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title


class EMIPayment(models.Model):
    plan = models.ForeignKey(EMIPlan, on_delete=models.CASCADE, related_name='payments')
    month_number = models.IntegerField()
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Month {self.month_number} - {'Paid' if self.is_paid else 'Pending'}"
class Salary(models.Model):
    employee_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100,default='Employee')
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.CharField(max_length=20)
    status = models.CharField(
        max_length=20,
        choices=[('Paid', 'Paid'), ('Pending', 'Pending')],
        default='Paid'
    )

    def __str__(self):
        return f"{self.employee_name} - {self.month}"
