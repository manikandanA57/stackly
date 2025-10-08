from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import JSONField
from django.contrib.auth.models import User
from django.utils import timezone


User = get_user_model()

class Branch(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Branch"
        verbose_name_plural = "Branches"

class Department(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL,null=True)
    code = models.CharField(max_length=50, unique=True)
    department_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) 

    def __str__(self):
        return self.department_name

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"

class Role(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='roles')
    role = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    permissions = models.JSONField(default=dict, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.role

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    profilePic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='primary_branch')
    available_branches = JSONField(blank=True, default=list)
    reporting_to = models.CharField(max_length=25, blank=True, null=True)
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    reset_token = models.CharField(max_length=32, blank=True, null=True)
    reset_token_expiry = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    




class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class TaxCode(models.Model):
    name = models.CharField(max_length=100, unique=True)
    percentage = models.FloatField()
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name

class UOM(models.Model):
    name = models.CharField(max_length=100, unique=True)
    items = models.IntegerField()
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name

class Warehouse(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=200)
    manager_name = models.CharField(max_length=100, blank=True)
    contact_info = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=100, unique=True)
    contact_person = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    def __str__(self):
        return self.name

class Product(models.Model):
    product_id = models.CharField(max_length=20, unique=True, editable=False, null=True, blank=True)
    name = models.CharField(max_length=100)
    product_type = models.CharField(
        max_length=50,
        choices=[('Goods', 'Goods'), ('Services', 'Services'), ('Combo', 'Combo')]
    )
    description = models.TextField(blank=True)

    # Foreign key + custom text fields
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    is_custom_category = models.BooleanField(default=False)
    custom_category = models.CharField(max_length=255, blank=True, null=True)

    tax_code = models.ForeignKey('TaxCode', on_delete=models.SET_NULL, null=True, blank=True)
    is_custom_tax_code = models.BooleanField(default=False)
    custom_tax_code = models.CharField(max_length=255, blank=True, null=True)

    uom = models.ForeignKey('UOM', on_delete=models.SET_NULL, null=True, blank=True)
    is_custom_uom = models.BooleanField(default=False)
    custom_uom = models.CharField(max_length=255, blank=True, null=True)

    warehouse = models.ForeignKey('Warehouse', on_delete=models.SET_NULL, null=True, blank=True)
    is_custom_warehouse = models.BooleanField(default=False)
    custom_warehouse = models.CharField(max_length=255, blank=True, null=True)

    size = models.ForeignKey('Size', on_delete=models.SET_NULL, null=True, blank=True)
    is_custom_size = models.BooleanField(default=False)
    custom_size = models.CharField(max_length=255, blank=True, null=True)

    color = models.ForeignKey('Color', on_delete=models.SET_NULL, null=True, blank=True)
    is_custom_color = models.BooleanField(default=False)
    custom_color = models.CharField(max_length=255, blank=True, null=True)

    supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL, null=True, blank=True)
    is_custom_supplier = models.BooleanField(default=False)
    custom_supplier = models.CharField(max_length=255, blank=True, null=True)

    related_products = models.CharField(max_length=1000, blank=True)
    is_custom_related_products = models.BooleanField(default=False)
    custom_related_products = models.CharField(max_length=255, blank=True, null=True)

    # Other fields
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    quantity = models.IntegerField(default=0)
    stock_level = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=0)
    weight = models.CharField(max_length=50, blank=True)
    specifications = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('Active', 'Active'), ('Inactive', 'Inactive'), ('Discontinued', 'Discontinued')]
    )
    product_usage = models.CharField(
        max_length=20,
        choices=[('Purchase', 'Purchase'), ('Sale', 'Sale'), ('Both', 'Both')]
    )
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    sub_category = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.product_id:
            self.product_id = f'CVB{self.id:03d}'
            Product.objects.filter(pk=self.pk).update(product_id=self.product_id)

    



from django.db import models
from django.db.models import JSONField
import re

class CandidateDocument(models.Model):
    file = models.FileField(upload_to='Candidate_documents/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CandidateDocument - {self.file.name}"

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"

class Candidate(models.Model):
    employee_code = models.CharField(max_length=10, unique=True, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey('Branch', on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.ForeignKey('Role', on_delete=models.SET_NULL, null=True, blank=True, related_name='candidate_designations')
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    joining_date = models.DateField(null=True, blank=True)
    personal_number = models.CharField(max_length=15)
    emergency_contact_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(unique=True)
    aadhar_number = models.CharField(max_length=14)
    pan_number = models.CharField(max_length=10)
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active')
    current_address = models.TextField(blank=True)
    highest_qualification = models.CharField(max_length=200, blank=True)
    previous_employer = models.CharField(max_length=200, blank=True)
    total_experience_year = models.PositiveIntegerField(null=True, blank=True)
    total_experience_month = models.PositiveIntegerField(null=True, blank=True)
    relevant_experience_year = models.PositiveIntegerField(null=True, blank=True)
    relevant_experience_month = models.PositiveIntegerField(null=True, blank=True)
    marital_status = models.CharField(max_length=20, choices=[('Married', 'Married'), ('Unmarried', 'Unmarried')], blank=True)
    basics = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hra = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    conveyance_allowance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    other_allowances = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    taxes = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pf = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    esi = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    uan_number = models.CharField(max_length=12, blank=True)
    pf_number = models.CharField(max_length=12, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=20, blank=True)
    ifsc_code = models.CharField(max_length=11, blank=True)
    asset = models.CharField(max_length=3, choices=[('Y', 'Yes'), ('N', 'No')], blank=True)
    asset_type = models.CharField(max_length=50, choices=[('laptop', 'Laptop'), ('phone', 'Phone')], blank=True)
    laptop_company_name = models.CharField(max_length=50, choices=[('HP', 'HP'), ('Dell', 'Dell'), ('Lenovo', 'Lenovo')], blank=True)
    asset_id = models.CharField(max_length=20, blank=True)
    upload_documents = models.ManyToManyField(CandidateDocument, blank=True)

    def save(self, *args, **kwargs):
        if not self.employee_code:
            last_candidate = Candidate.objects.order_by('id').last()
            if last_candidate:
                last_num = int(last_candidate.employee_code.replace('STA', ''))
                new_num = last_num + 1
            else:
                new_num = 1
            self.employee_code = f'STA{new_num:04d}'

        # Validate phone numbers
        phone_regex = r'^[0-9+\-\s]+$'
        if self.personal_number and not re.match(phone_regex, self.personal_number):
            raise ValueError("Personal number must contain only digits, +, -, or spaces.")
        if self.emergency_contact_number and not re.match(phone_regex, self.emergency_contact_number):
            raise ValueError("Emergency contact number must contain only digits, +, -, or spaces.")

        # Validate Aadhar number
        aadhar_regex = r'^\d{4}\s?\d{4}\s?\d{4}$'
        if not re.match(aadhar_regex, self.aadhar_number):
            raise ValueError("Aadhar number must be 12 digits, optionally with spaces.")

        # Validate PAN number
        pan_regex = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        if not re.match(pan_regex, self.pan_number):
            raise ValueError("PAN number must be 5 letters, 4 digits, 1 letter (e.g., ABCDE1234F).")

        # Validate account number
        if self.account_number and not self.account_number.isdigit():
            raise ValueError("Account number must contain only digits.")

        # Validate asset-related fields
        if self.asset == 'Y' and not self.asset_type:
            raise ValueError("Asset type is required when asset is Yes.")
        if self.asset_type == 'laptop' and not self.laptop_company_name:
            raise ValueError("Laptop company name is required when asset type is laptop.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee_code} - {self.first_name} {self.last_name}"




class GovernmentHoliday(models.Model):
    date = models.DateField(unique=True)
    description = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.date} - {self.description}"

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    check_in_times = models.JSONField(default=list)  # Array of check-in/check-out timestamps
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.total_hours} hrs"
    

from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Awaiting Feedback', 'Awaiting Feedback')
    ])
    start_date = models.DateField()
    due_date = models.DateField()
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks_assigned')
    priority = models.CharField(max_length=20, choices=[
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High')
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    



class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    customer_type = models.CharField(max_length=50, choices=[
        ('Individual', 'Individual'),
        ('Business', 'Business'),
        ('Organization', 'Organization'),
    ])
    customer_id = models.CharField(max_length=10, unique=True, null=True, blank=True)  # Added blank=True
    status = models.CharField(max_length=20, choices=[
        ('Active', 'Active'),
        ('Inactive', 'Inactive')
    ])
    assigned_sales_rep = models.ForeignKey(
    Candidate,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
)

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    gst_tax_id = models.CharField(max_length=20, blank=True)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    available_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True)  
    billing_address = models.TextField(blank=True)
    shipping_address = models.TextField(blank=True)
    payment_terms = models.CharField(max_length=50, blank=True)
    credit_term = models.CharField(max_length=50, blank=True)
    last_edit_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.customer_id})"
        

