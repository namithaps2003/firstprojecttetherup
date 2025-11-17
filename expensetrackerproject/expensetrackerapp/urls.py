from django.urls import path,include
from . import views
from django.conf import settings       # ✅ Import settings
from django.conf.urls.static import static 

urlpatterns = [
    path('addexpense',views.addexpense,name='addexpense'),    
    path('homepage',views.viewexpenses,name='viewexpenses'),
    path('updateexpense/<int:id>',views.update_expense,name='updateexpense'),
    path('deleteexpense/<int:id>', views.deleteentry, name='deleteentry'),
    path('homepage2', views.homepage2, name='homepage2'),
    path('firsthomepage', views.firsthomepage, name='firsthomepage'),
    path('', views.index, name='index'),
    path('addsalary', views.addsalary, name='addsalary'),
    path('billview', views.billview, name='billview'),
    path('billview2', views.billview2, name='billview2'),
     path('hii', views.invoice_page, name='invoice_page'),
    path('generate_pdf/', views.generate_pdf, name='generate_pdf'),
    path('generate_pdf2/', views.generate_pdf2, name='generate_pdf2'),
    path('emi/create/', views.create_emi, name='create_emi'),
    path('emilist/', views.emi_list, name='emi_list'),
    path('emi/status/<int:plan_id>/', views.emi_status, name='emi_status'),
    path('emi/mark_paid/<int:payment_id>/', views.mark_paid, name='mark_paid'),
    path('emi/delete/<int:plan_id>/', views.delete_emi, name='delete_emi'),
    path('salary_status', views.salary_status, name='salary_status'),
    path('logout/', views.logout_view, name='logout'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)