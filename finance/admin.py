from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Person)
admin.site.register(Diposit)
admin.site.register(PremiumCollectionRecord)
admin.site.register(Loan)
admin.site.register(LoanRecovery)
admin.site.register(User)