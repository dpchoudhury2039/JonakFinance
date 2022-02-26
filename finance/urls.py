from django.urls import include, path

from .views import *

app_name = 'finance'

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('login', Login.as_view(), name='login'),
    path('logout', Logout.as_view(), name='logout'),
    path('persons', PersonList.as_view(), name='persons'),
    path('addPerson', AddPerson.as_view(), name='add-person'),
    path('dipositors', DipositorList.as_view(), name='dipositors'),
    path('addDipositor', AddDipositor.as_view(), name='add-dipositor'),
    path('premiumCollectionList/<int:account_id>/', PremiumCollectionList.as_view(), name='premium-collection-list'),
    path('todayPremiumCollection/', TodayPremiumCollection.as_view(), name='today-premium-collection-list'),
    path('todayPremiumCollectionPDF/', TodayPremiumCollectionPDF.as_view(), name='today-premium-collection-pdf'),
    path('collectPremium/', CollectPremium.as_view(), name='collect-premium'),
    path('loans', LoanList.as_view(), name='loans'),
    path('addLoan', AddLoan.as_view(), name='add-loan'),
    path('loanRecoveryList/<int:loan_id>/', LoanRecoveryList.as_view(), name='loan-recovery-list'),
    path('todayLoanRecoveryList/', TodayLoanRecoveryList.as_view(), name='today-loan-recovery-list'),
    path('todayLoanRecoveryPDF/', TodayLoanRecoveryPDF.as_view(), name='today-loan-recovery-pdf'),
    path('loanRecovery/', RecoverLoan.as_view(), name='loan-recovery'),
    path('userList/', UserList.as_view(), name='user-list'),
    path('userTodayCollectionList/<int:user_id>/', UserTodayCollectionList.as_view(), name='user-today-collection-list'),
    path('TodayCollectionList/', TodayCollectionList.as_view(), name='today-collection-list'),
]