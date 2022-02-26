import random
import datetime as DT

from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView

from .models import *
#from .render import Render

class Login(TemplateView):
    template_name = "app/login.html"

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user_obj = User.objects.get(username=username, password=password)
            request.session['userLoggedInName'] = user_obj.name
            request.session['userLoggedInRole'] = user_obj.role
            request.session['userLoggedInID'] = user_obj.id
            return HttpResponseRedirect(reverse('finance:home'))
        except:
            url = "%s?error=1" % reverse("finance:login")
            return HttpResponseRedirect(url)

class Logout(View):

    def get(self, request):
        try:
            for key in list(request.session.keys()):
                del request.session[key]
        except KeyError:
            pass
        url = "%s?logout=1" % reverse("finance:login")
        return HttpResponseRedirect(url)


class Home(TemplateView):
    template_name = "app/index.html"

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        loan_obj = Loan.objects.filter(recovered=False)
        totalLoanAmount = 0
        for loan in loan_obj:
            totalLoanAmount = totalLoanAmount + loan.outstanding
        context['totalLoanAmount'] = totalLoanAmount

        totalDipositAmount = 0
        PremiumCollectionRecord_obj = PremiumCollectionRecord.objects.filter(diposit__withdrawn = False, collected=True)
        for PremiumCollectionRecord_ins in PremiumCollectionRecord_obj:
            totalDipositAmount = totalDipositAmount + PremiumCollectionRecord_ins.diposit.premium
        context['totalDipositAmount'] = totalDipositAmount

        today = DT.date.today()
        today_premium_collection_obj = PremiumCollectionRecord.objects.filter(collectedDate=today)

        today_total_premium_collection = 0
        for today_premium_collection in today_premium_collection_obj:
            today_total_premium_collection = today_total_premium_collection + today_premium_collection.diposit.premium
        context['today_total_premium_collection'] = today_total_premium_collection

        today_loan_recovery_obj = LoanRecovery.objects.filter(collectedDate=today)
        today_installment_collection = 0

        for today_loan_recovery in today_loan_recovery_obj:
            today_installment_collection = today_installment_collection + today_loan_recovery.loan.installment
        context['today_installment_collection'] = today_installment_collection
        return context

class PersonList(ListView):
    model = Person
    template_name = "app/PersonList.html"
    context_object_name = "persons"


class AddPerson(CreateView):
    # specify the model for create view
    model = Person
    fields = ['first_name', 'last_name', 'phone_no']
    template_name = "app/AddPerson.html"


class DipositorList(ListView):
    model = Diposit
    template_name = "app/dipositorList.html"
    context_object_name = "diposits"


class AddDipositor(TemplateView):
    template_name = "app/addDipositor.html"

    def get_context_data(self, **kwargs):
        context = super(AddDipositor, self).get_context_data(**kwargs)
        context['persons'] = Person.objects.all()
        return context

    def post(self, request):
        dipositorID = request.POST.get('dipositorID')
        date = request.POST.get('date')
        place = request.POST.get('place')
        interest = request.POST.get('interest')
        pMode = request.POST.get('pMode')
        duration = request.POST.get('duration')
        premium = request.POST.get('premium')

        date = DT.datetime.strptime(date, "%d/%m/%Y")
        account_id = random.randint(100000, 999999)
        person_obj = Person.objects.get(id = dipositorID)
        Diposit_obj = Diposit.objects.create(account_id=account_id, dipositorName=person_obj, place=place, date = date, interest=interest,
                               pMode=pMode, duration=duration, premium=premium)

        startDate = request.POST.get('startDate')
        startDate = DT.datetime.strptime(startDate, "%d/%m/%Y")
        PremiumCollectionRecord.objects.create(diposit=Diposit_obj, date=startDate)
        for i in range(1, int(duration)):
            if pMode == "Daily":
                next_date = startDate + DT.timedelta(days=i)
            elif pMode == "Weekly":
                next_date = startDate + DT.timedelta(days=7*i)
            elif pMode == "Fortnightly":
                next_date = startDate + DT.timedelta(days=15*i)
            elif pMode == "Monthly":
                next_date = startDate + DT.timedelta(days=30*i)
            PremiumCollectionRecord.objects.create(diposit=Diposit_obj, date=next_date)

        return HttpResponseRedirect(reverse('finance:dipositors'))


class CollectPremium(View):
    def post(self, request):
        id = request.POST.get('id')
        place = request.POST.get('place')
        amount = request.POST.get('amount')
        premiumCollectionRecord_obj = PremiumCollectionRecord.objects.get(id=id)
        premiumCollectionRecord_obj.collected = True
        premiumCollectionRecord_obj.collectionPlace = place
        premiumCollectionRecord_obj.collectedAmount = amount
        today = DT.date.today()
        premiumCollectionRecord_obj.collectedDate = today
        user_obj = User.objects.get(id=request.session['userLoggedInID'])
        premiumCollectionRecord_obj.collector = user_obj
        premiumCollectionRecord_obj.save()

        premiumCollected_obj = PremiumCollectionRecord.objects.filter(diposit=premiumCollectionRecord_obj.diposit, collected=True)
        sumAssured = 0
        for premiumCollected in premiumCollected_obj:
            sumAssured = sumAssured + premiumCollected.diposit.premium
            date = premiumCollected.collectedDate

        delta = date - premiumCollectionRecord_obj.diposit.date
        year = delta.days/365
        sumAssured = sumAssured + (sumAssured*premiumCollectionRecord_obj.diposit.interest*year)/100
        print("sumAssured", sumAssured)

        diposit_obj = Diposit.objects.get(id=premiumCollectionRecord_obj.diposit.id)
        diposit_obj.sumAssured = round(sumAssured, 2)
        diposit_obj.save()
        return HttpResponseRedirect(reverse('finance:premium-collection-list', kwargs={'account_id': premiumCollectionRecord_obj.diposit.account_id}))


class PremiumCollectionList(ListView):
    model = PremiumCollectionRecord
    template_name = "app/premiumCollectionList.html"

    def get_context_data(self, **kwargs):
        context = super(PremiumCollectionList, self).get_context_data(**kwargs)
        diposit_obj = Diposit.objects.get(account_id = self.kwargs["account_id"])
        context['premiumCollections'] = PremiumCollectionRecord.objects.filter(diposit = diposit_obj)
        return context

class TodayPremiumCollection(ListView):
    model = PremiumCollectionRecord
    template_name = "app/todayPremiumCollectionList.html"

    def get_context_data(self, **kwargs):
        context = super(TodayPremiumCollection, self).get_context_data(**kwargs)
        today = DT.date.today()
        context['todayPremiumCollections'] = PremiumCollectionRecord.objects.filter(collectedDate = today)
        today_premium_collection_obj = PremiumCollectionRecord.objects.filter(collectedDate = today)

        today_total_collection = 0
        for today_premium_collection in today_premium_collection_obj:
            today_total_collection = today_total_collection + today_premium_collection.diposit.premium
        context['today_total_collection'] = today_total_collection
        return context


class TodayPremiumCollectionPDF(ListView):
    model = PremiumCollectionRecord
    template_name = "app/todayPremiumCollectionPDF.html"

    def get_context_data(self, **kwargs):
        context = super(TodayPremiumCollectionPDF, self).get_context_data(**kwargs)
        today = DT.date.today()
        context['today'] = today
        context['todayPremiumCollections'] = PremiumCollectionRecord.objects.filter(collectedDate = today)
        today_premium_collection_obj = PremiumCollectionRecord.objects.filter(collectedDate = today)

        today_total_collection = 0
        for today_premium_collection in today_premium_collection_obj:
            today_total_collection = today_total_collection + today_premium_collection.diposit.premium
        context['today_total_collection'] = today_total_collection
        return context


class LoanList(ListView):
    model = Loan
    template_name = "app/loanList.html"
    context_object_name = "loans"


class AddLoan(TemplateView):
    template_name = "app/addLoan.html"

    def get_context_data(self, **kwargs):
        context = super(AddLoan, self).get_context_data(**kwargs)
        context['persons'] = Person.objects.all()
        return context

    def post(self, request):
        loaner_id = request.POST.get('loaner_id')
        date = request.POST.get('date')
        place = request.POST.get('place')
        amount = request.POST.get('amount')
        interest = request.POST.get('interest')
        pMode = request.POST.get('pMode')
        duration = request.POST.get('duration')
        installment = request.POST.get('installment')
        outstanding = request.POST.get('outstanding')

        date = DT.datetime.strptime(date, "%d/%m/%Y")
        account_id = random.randint(100000, 999999)
        person_obj = Person.objects.get(id = loaner_id)
        loan_obj = Loan.objects.create(loan_id=account_id, date=date, place=place, loanerName=person_obj, amount=amount, interest=interest,
                               pMode=pMode, duration=duration, installment=installment, outstanding=outstanding)

        startDate = request.POST.get('startDate')
        startDate = DT.datetime.strptime(startDate, "%d/%m/%Y")
        LoanRecovery.objects.create(loan=loan_obj, date=startDate)
        for i in range(1, int(duration)):
            if pMode == "Daily":
                next_date = startDate + DT.timedelta(days=i)
            elif pMode == "Weekly":
                next_date = startDate + DT.timedelta(days=7 * i)
            elif pMode == "Fortnightly":
                next_date = startDate + DT.timedelta(days=15 * i)
            elif pMode == "Monthly":
                next_date = startDate + DT.timedelta(days=30 * i)
            LoanRecovery.objects.create(loan=loan_obj, date=next_date)

        return HttpResponseRedirect(reverse('finance:loans'))


class LoanRecoveryList(ListView):
    model = LoanRecovery
    template_name = "app/loanRecoveryList.html"

    def get_context_data(self, **kwargs):
        context = super(LoanRecoveryList, self).get_context_data(**kwargs)
        loan_obj = Loan.objects.get(loan_id = self.kwargs["loan_id"])
        context['LoanRecoverys'] = LoanRecovery.objects.filter(loan = loan_obj)
        return context


class TodayLoanRecoveryList(ListView):
    model = LoanRecovery
    template_name = "app/todayLoanRecoveryList.html"

    def get_context_data(self, **kwargs):
        context = super(TodayLoanRecoveryList, self).get_context_data(**kwargs)
        today = DT.date.today()
        context['TodayLoanRecoverys'] = LoanRecovery.objects.filter(collectedDate = today)
        today_loan_recovery_obj = LoanRecovery.objects.filter(collectedDate=today)
        today_total_collection = 0

        for today_loan_recovery in today_loan_recovery_obj:
            today_total_collection = today_total_collection + today_loan_recovery.loan.installment
        context['today_total_collection'] = today_total_collection
        return context


class TodayLoanRecoveryPDF(ListView):
    model = LoanRecovery
    template_name = "app/todayLoanRecoveryPDF.html"

    def get_context_data(self, **kwargs):
        context = super(TodayLoanRecoveryPDF, self).get_context_data(**kwargs)
        today = DT.date.today()
        context['today'] = today
        context['TodayLoanRecoverys'] = LoanRecovery.objects.filter(collectedDate=today)
        today_loan_recovery_obj = LoanRecovery.objects.filter(collectedDate=today)
        today_total_collection = 0

        for today_loan_recovery in today_loan_recovery_obj:
            today_total_collection = today_total_collection + today_loan_recovery.loan.installment
        context['today_total_collection'] = today_total_collection
        return context

class RecoverLoan(View):
    def post(self, request):
        id = request.POST.get('id')
        place = request.POST.get('place')
        amount = request.POST.get('amount')

        LoanRecovery_obj = LoanRecovery.objects.get(id=id)
        LoanRecovery_obj.collected = True
        LoanRecovery_obj.collectionPlace = place
        LoanRecovery_obj.collectedAmount = amount
        today = DT.date.today()
        LoanRecovery_obj.collectedDate = today
        user_obj = User.objects.get(id=request.session['userLoggedInID'])
        LoanRecovery_obj.collector = user_obj
        LoanRecovery_obj.save()
        return HttpResponseRedirect(reverse('finance:loan-recovery-list', kwargs={'loan_id': LoanRecovery_obj.loan.loan_id}))


class UserList(ListView):
    model = User
    context_object_name = "users"
    template_name = "app/userList.html"


class UserTodayCollectionList(ListView):
    model = LoanRecovery
    template_name = "app/userTodayCollectionList.html"

    def get_context_data(self, **kwargs):
        context = super(UserTodayCollectionList, self).get_context_data(**kwargs)

        user_obj = User.objects.get(id=self.kwargs["user_id"])
        today = DT.date.today()
        context['TodayLoanRecoverys'] = LoanRecovery.objects.filter(collectedDate=today, collector=user_obj)
        today_loan_recovery_obj = LoanRecovery.objects.filter(collectedDate=today, collector=user_obj)
        today_total_collection = 0
        for today_loan_recovery in today_loan_recovery_obj:
            today_total_collection = today_total_collection + today_loan_recovery.loan.installment
        context['today_loan_total_collection'] = today_total_collection



        context['todayPremiumCollections'] = PremiumCollectionRecord.objects.filter(collectedDate=today, collector=user_obj)
        today_premium_collection_obj = PremiumCollectionRecord.objects.filter(collectedDate=today, collector=user_obj)

        today_total_collection = 0
        for today_premium_collection in today_premium_collection_obj:
            today_total_collection = today_total_collection + today_premium_collection.diposit.premium
        context['today_premium_total_collection'] = today_total_collection
        return context


class TodayCollectionList(ListView):
    model = LoanRecovery
    template_name = "app/todayCollectionList.html"

    def get_context_data(self, **kwargs):
        context = super(TodayCollectionList, self).get_context_data(**kwargs)

        today = DT.date.today()
        context['TodayLoanRecoverys'] = LoanRecovery.objects.filter(collectedDate=today)
        today_loan_recovery_obj = LoanRecovery.objects.filter(collectedDate=today)
        today_total_collection = 0
        for today_loan_recovery in today_loan_recovery_obj:
            today_total_collection = today_total_collection + today_loan_recovery.loan.installment
        context['today_loan_total_collection'] = today_total_collection
        today_total_loan_collection = today_total_collection



        context['todayPremiumCollections'] = PremiumCollectionRecord.objects.filter(collectedDate=today)
        today_premium_collection_obj = PremiumCollectionRecord.objects.filter(collectedDate=today)

        today_total_collection = 0
        for today_premium_collection in today_premium_collection_obj:
            today_total_collection = today_total_collection + today_premium_collection.diposit.premium
        context['today_premium_total_collection'] = today_total_collection
        today_total_premium_collection = today_total_collection
        context['today_total_collection'] = today_total_loan_collection + today_total_premium_collection
        return context