from django.db import models
from django.urls import reverse


ROLE_CHOICES = (
    ('Staff', 'Staff'),
    ('Admin', 'Admin'),
)


class User(models.Model):
    name = models.CharField(blank=False, max_length=30)
    username = models.CharField(blank=False, max_length=30, unique=True)
    password = models.CharField(blank=False, max_length=30)
    role = models.CharField(max_length=6, choices=ROLE_CHOICES, default='Staff')

    def __str__(self):
        return self.name


class Person(models.Model):
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    phone_no = models.IntegerField(blank=False)

    def __str__(self):
        return self.first_name + " " + self.last_name

    def get_absolute_url(self):
        return reverse('finance:persons')


class Diposit(models.Model):
    account_id = models.IntegerField(blank=False, unique=True)
    date = models.DateField(blank=False, null=False)
    dipositorName = models.ForeignKey(Person, on_delete=models.CASCADE)
    amount = models.FloatField(blank=False)
    interest = models.FloatField(blank=False)
    pMode = models.CharField(blank=False, max_length=30)
    duration = models.IntegerField(blank=False)
    premium = models.FloatField(default=False)
    sumAssured = models.FloatField(blank=True, null=True)
    withdrawn = models.BooleanField(default=False)

    def __str__(self):
        return self.dipositorName.first_name + " " + self.dipositorName.last_name + " (" + str(self.account_id) + ")"


class PremiumCollectionRecord(models.Model):
    diposit = models.ForeignKey(Diposit, on_delete=models.CASCADE)
    date = models.DateField(blank=False)
    collected = models.BooleanField(default=False)
    collectedDate = models.DateField(blank=True, null=True)
    collector = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    collectionPlace = models.CharField(blank=True, max_length=30)

    def __str__(self):
        return self.diposit.dipositorName.first_name + " " + self.diposit.dipositorName.last_name + " (" + str(
            self.diposit.account_id) + ")" + "(" + str(self.date) + ")"


class Loan(models.Model):
    loan_id = models.IntegerField(blank=False, unique=True)
    date = models.DateField(blank=False, null=False)
    loanerName = models.ForeignKey(Person, on_delete=models.CASCADE)
    amount = models.FloatField(blank=False)
    interest = models.FloatField(blank=False)
    installment = models.FloatField(blank=False)
    duration = models.IntegerField(blank=False)
    recovered = models.BooleanField(default=False)
    pMode = models.CharField(blank=False, max_length=30)
    outstanding = models.FloatField(blank=False)

    def __str__(self):
        return self.loanerName.first_name + " " + self.loanerName.last_name + " (" + str(self.loan_id) + ")"


class LoanRecovery(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    date = models.DateField(blank=False)
    collected = models.BooleanField(default=False)
    collectedDate = models.DateField(blank=True, null=True)
    collector = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    collectionPlace = models.CharField(blank=True, max_length=30)

    def __str__(self):
        return self.loan.loanerName.first_name + " " + self.loan.loanerName.last_name + " (" + str(
            self.loan.loan_id) + ")" + "(" + str(self.date) + ")"