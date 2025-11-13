

from django.contrib import admin
from.models import ExpenseEntry,EMIPayment,EMIPlan,Salary
admin.site.register(ExpenseEntry)
admin.site.register(EMIPlan)
admin.site.register(EMIPayment)
admin.site.register(Salary)