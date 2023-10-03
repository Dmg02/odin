from django.db import models
from .choices import LAW_BRANCH_CHOICES, TRIAL_TYPE_CHOICES, AMPARO_TYPE_CHOICES, LEGAL_PARTY_TYPE_CHOICES, ORGANIZATION_STATUS_CHOICES, USER_ROLE_CHOICES
# Common Tables
class State(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

class City(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

class LawBranch(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, choices=LAW_BRANCH_CHOICES)

class Authority(models.Model):
    id = models.AutoField(primary_key=True)
    law_branch = models.ForeignKey(LawBranch, on_delete=models.CASCADE)
    competencia = models.CharField(max_length=100)
    circuito = models.CharField(max_length=100)
    description = models.TextField()
    parent_authority = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='child_authorities')

class TrialType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, choices=TRIAL_TYPE_CHOICES, null=True, blank=True)

class LegalParty(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True) 
    last_name_2 = models.CharField(max_length=100, null=True, blank=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    party_type = models.CharField(max_length=10, choices=LEGAL_PARTY_TYPE_CHOICES)

class Trial(models.Model):
    id = models.AutoField(primary_key=True)
    law_branch = models.ForeignKey(LawBranch, on_delete=models.CASCADE)
    authority = models.ForeignKey(Authority, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    trial_type = models.ForeignKey(TrialType, on_delete=models.CASCADE)
    case_number = models.CharField(max_length=100)
    parties = models.ManyToManyField(LegalParty, through='TrialParty')

class TrialParty(models.Model):
    trial = models.ForeignKey(Trial, on_delete=models.CASCADE)
    legal_party = models.ForeignKey(LegalParty, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)

class LegalProceedingGeneral(models.Model):
    id = models.AutoField(primary_key=True)
    trial = models.ForeignKey(Trial, on_delete=models.CASCADE)
    publication_date = models.DateField()
    agreement_date = models.DateField()
    summary = models.TextField()

class AmparoType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, choices=AMPARO_TYPE_CHOICES)

class AmparoLegalProceeding(models.Model):
    id = models.AutoField(primary_key=True)
    publication_date = models.DateField()
    agreement_date = models.DateField()
    summary = models.TextField()
    amparo_trial_common = models.ForeignKey('AmparoTrialCommon', on_delete=models.CASCADE)

class AmparoTrialParty(models.Model):
    amparo_trial = models.ForeignKey('AmparoTrialCommon', on_delete=models.CASCADE)
    legal_party = models.ForeignKey(LegalParty, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)

class AmparoTrialCommon(models.Model):
    id = models.AutoField(primary_key=True)
    trial = models.ForeignKey('Trial', related_name='amparo_trials', on_delete=models.CASCADE)
    amparo_type = models.ForeignKey('AmparoType', on_delete=models.CASCADE)
    parties = models.ManyToManyField(LegalParty, through='AmparoTrialParty')
    amparo_legal_proceedings = models.ManyToManyField('AmparoLegalProceeding', related_name='amparo_trials')

# Tenant-Specific Tables

class Organization(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    azure_ad_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=ORGANIZATION_STATUS_CHOICES)

class User(models.Model):
    id = models.AutoField(primary_key=True)
    azure_ad_id = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=ORGANIZATION_STATUS_CHOICES)
    role = models.CharField(max_length=20, choices=USER_ROLE_CHOICES)

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    group_id = models.CharField(max_length=100)
    date_added = models.DateField()
    parent_customer = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='child_customers')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_customers')

class TenantTrial(models.Model):
    id = models.AutoField(primary_key=True)
    trial = models.ForeignKey(Trial, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    users = models.ManyToManyField(User)
    customer = models.ForeignKey(Customer,related_name='tenant_trials',blank=True,null=True, on_delete=models.SET_NULL)
    amparo_trial = models.ForeignKey('AmparoTrialTenant', related_name='amparo_trial_tenant', blank=True, null=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tenant_trials')
    legal_proceeding_general = models.ForeignKey('tenant_legal_proceeding', related_name='general_tenant_trials', null=True, blank=True, on_delete=models.SET_NULL)
    tenant_legal_proceedings = models.ManyToManyField('tenant_legal_proceeding', related_name='m2m_tenant_trials')

class AmparoTrialTenant(models.Model):
    id = models.AutoField(primary_key=True)
    amparo_trial_common = models.ForeignKey(AmparoTrialCommon, related_name='tenant_amparo_trials', on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    users = models.ManyToManyField(User)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_amparo_tenant_trials')

class Document(models.Model):
    id = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=100)
    file_type = models.CharField(max_length=10)
    azure_blob_url = models.CharField(max_length=200)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_date = models.DateField()
    edited_by = models.ForeignKey(User, related_name='edited_documents', null=True, blank=True, on_delete=models.SET_NULL)
    edited_by_date = models.DateField(null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    tenant_trial = models.ForeignKey('TenantTrial', related_name='documents', null=True, blank=True, on_delete=models.SET_NULL)
    amparo_trial_tenant = models.ForeignKey('AmparoTrialTenant', related_name='documents', null=True, blank=True, on_delete=models.SET_NULL)
    tenant_legal_proceeding = models.ForeignKey('tenant_legal_proceeding', related_name='documents', null=True, blank=True, on_delete=models.SET_NULL)
    description = models.TextField() #brief description of the document
   

class tenant_legal_proceeding(models.Model):
    id = models.AutoField(primary_key=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    trial = models.ForeignKey(TenantTrial, on_delete=models.CASCADE)
    publication_date = models.DateField()
    agreement_date = models.DateField()
    summary = models.TextField()
    document = models.ForeignKey(Document, related_name='related_legal_proceedings', on_delete=models.CASCADE)

class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    users = models.ManyToManyField(User, related_name='notifications')
    message = models.TextField()
    status = models.CharField(max_length=10, choices=[('Read', 'Read'), ('Unread', 'Unread')])
    email_status = models.CharField(max_length=15, choices=[('Sent', 'Sent'), ('Failed', 'Failed'), ('Opened', 'Opened')], null=True, blank=True)
    sendgrid_message_id = models.CharField(max_length=50, null=True, blank=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    opened_date = models.DateTimeField(null=True, blank=True)
    trial = models.ForeignKey(Trial, related_name='notifications', null=True, blank=True, on_delete=models.SET_NULL)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

class Subscription(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trial = models.ForeignKey(Trial, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')])
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_subscriptions')
    amparo_trial_tenant = models.ForeignKey('AmparoTrialTenant', related_name='subscriptions', null=True, blank=True, on_delete=models.SET_NULL)

class InquerieType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_inqueries')

class InqueriesMatter(models.Model):
    id = models.AutoField(primary_key=True)
    inquerie_type = models.ForeignKey(InquerieType, on_delete=models.CASCADE)
    description = models.TextField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_inqueries_matters')
