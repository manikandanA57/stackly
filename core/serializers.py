from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Department, Branch, Role, Candidate

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name']

class DepartmentDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'department_name']

class DepartmentSerializer(serializers.ModelSerializer):
    branch = BranchSerializer(read_only=True)
    roles = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'code', 'department_name', 'branch', 'description', 'roles']

    def get_roles(self, obj):
        if self.context.get('include_roles', True):
            return RoleSerializer(obj.roles.all(), many=True).data
        return []

class DepartmentCreateSerializer(serializers.ModelSerializer):
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())  # Mandatory

    class Meta:
        model = Department
        fields = ['id', 'code', 'department_name', 'branch', 'description']

class RoleSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.department_name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'role', 'description', 'permissions', 'department_name', 'branch_name']

class RoleUpdateSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())  # Mandatory
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())  # Mandatory
    department_name = serializers.CharField(source='department.department_name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    description = serializers.CharField(required=False, allow_blank=True)
    permissions = serializers.JSONField(required=False, allow_null=True, default=dict)

    class Meta:
        model = Role
        fields = ['id', 'role', 'description', 'permissions', 'department', 'department_name', 'branch', 'branch_name']

    def validate_permissions(self, value):
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise serializers.ValidationError("Permissions must be a valid JSON object.")
        return value



class ProfileDetailSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    branch = BranchSerializer(read_only=True)
    available_branches = serializers.ListField(child=serializers.CharField(), read_only=True)
    reporting_to = serializers.CharField(allow_null=True, read_only=True)
    role = RoleSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = [
            'role', 'profilePic', 'contact_number', 'department',
            'branch', 'available_branches', 'reporting_to', 'employee_id'
        ]

class ProfileUpdateSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), allow_null=True)
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), allow_null=True)
    available_branches = serializers.ListField(child=serializers.CharField(), required=False)
    reporting_to = serializers.CharField(allow_null=True, read_only=True)
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), allow_null=True)
    profilePic = serializers.ImageField(allow_empty_file=True, required=False)
    contact_number = serializers.CharField(max_length=15, allow_blank=True, allow_null=True)

    class Meta:
        model = Profile
        fields = [
            'role', 'profilePic', 'contact_number', 'department',
            'branch', 'available_branches', 'reporting_to', 'employee_id'
        ]

    def validate_contact_number(self, value):
        if value and not value.replace("+", "").replace("-", "").replace(" ", "").isdigit():
            raise serializers.ValidationError("Contact number must contain only digits, +, -, or spaces.")
        return value

    def validate_employee_id(self, value):
        if value and self.instance:
            if self.instance.employee_id == value:
                return value
            if Profile.objects.exclude(pk=self.instance.pk).filter(employee_id=value).exists():
                raise serializers.ValidationError("Employee ID must be unique.")
        elif value:
            if Profile.objects.filter(employee_id=value).exists():
                raise serializers.ValidationError("Employee ID must be unique.")
        return value

    
class UserSerializer(serializers.ModelSerializer):
    profile = ProfileDetailSerializer()

    class Meta:
        model = User
        fields = ['first_name', 'email', 'password', 'profile']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data.get('password'),  # Default to empty if not provided
            first_name=validated_data['first_name']
        )
        Profile.objects.create(user=user, **profile_data)
        return user

# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    remember_me = serializers.BooleanField(default=True)  # Checkbox defaults to checked

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        if not any(c.isdigit() for c in data['new_password']) or not any(c.isalpha() for c in data['new_password']):
            raise serializers.ValidationError("Password must contain at least one number and one alphabet")
        return data

class ManageUserSerializer(serializers.ModelSerializer):
    profile = ProfileDetailSerializer()
    code = serializers.CharField(source='id', read_only=True)
    last_name = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = User
        fields = ['code', 'email', 'first_name', 'last_name', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()

        profile = instance.profile
        profile.contact_number = profile_data.get('contact_number', profile.contact_number)
        profile.branch = profile_data.get('branch', profile.branch)
        profile.department = profile_data.get('department', profile.department)
        profile.role = profile_data.get('role', profile.role)
        profile.reporting_to = profile_data.get('reporting_to', profile.reporting_to)
        profile.available_branches = profile_data.get('available_branches', profile.available_branches)
        profile.profilePic = profile_data.get('profilePic', profile.profilePic)
        profile.save()

        return instance

class CreateUserSerializer(serializers.ModelSerializer):
    profile = ProfileUpdateSerializer()
    last_name = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'profile']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
        }

    def validate_email(self, value):
        if self.instance:  # Update mode
            if self.instance.email == value:
                return value  # Skip uniqueness check for same value
            if User.objects.exclude(pk=self.instance.pk).filter(username=value).exists():
                raise serializers.ValidationError("A user with this email already exists.")
        else:  # Create mode
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        password = validated_data.pop('password', None)

        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=password if password else '',
            first_name=validated_data['first_name'],
            last_name=validated_data.get('last_name', '')
        )

        available_branches = profile_data.pop('available_branches', [])
        profile = Profile.objects.create(user=user, **profile_data)
        profile.available_branches = available_branches
        profile.save()

        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()

        profile = instance.profile
        profile.contact_number = profile_data.get('contact_number', profile.contact_number)
        profile.branch = profile_data.get('branch', profile.branch)
        profile.department = profile_data.get('department', profile.department)
        profile.role = profile_data.get('role', profile.role)
        profile.reporting_to = profile_data.get('reporting_to', profile.reporting_to)
        profile.available_branches = profile_data.get('available_branches', profile.available_branches)
        profile.profilePic = profile_data.get('profilePic', profile.profilePic)
        profile.save()

        return instance



class ProfileChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

from rest_framework import serializers
from .models import Product, Category, TaxCode, UOM, Warehouse, Size, Color, Supplier

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class TaxCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxCode
        fields = ['id', 'name', 'percentage', 'description']

class UOMSerializer(serializers.ModelSerializer):
    class Meta:
        model = UOM
        fields = ['id', 'name', 'items', 'description']

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'location', 'manager_name', 'contact_info', 'notes']

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name']

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name']

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_person', 'phone_number', 'email', 'address']

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False, allow_null=True)
    tax_code = serializers.PrimaryKeyRelatedField(queryset=TaxCode.objects.all(), required=False, allow_null=True)
    uom = serializers.PrimaryKeyRelatedField(queryset=UOM.objects.all(), required=False, allow_null=True)
    warehouse = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.all(), required=False, allow_null=True)
    size = serializers.PrimaryKeyRelatedField(queryset=Size.objects.all(), required=False, allow_null=True)
    color = serializers.PrimaryKeyRelatedField(queryset=Color.objects.all(), required=False, allow_null=True)
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all(), required=False, allow_null=True)
    related_products = serializers.CharField(max_length=1000, required=False, allow_blank=True)

    # Custom fields for each dropdown
    is_custom_category = serializers.BooleanField(default=False, required=False)
    custom_category = serializers.CharField(max_length=255, required=False, allow_blank=True)
    is_custom_tax_code = serializers.BooleanField(default=False, required=False)
    custom_tax_code = serializers.CharField(max_length=255, required=False, allow_blank=True)
    is_custom_uom = serializers.BooleanField(default=False, required=False)
    custom_uom = serializers.CharField(max_length=255, required=False, allow_blank=True)
    is_custom_warehouse = serializers.BooleanField(default=False, required=False)
    custom_warehouse = serializers.CharField(max_length=255, required=False, allow_blank=True)
    is_custom_size = serializers.BooleanField(default=False, required=False)
    custom_size = serializers.CharField(max_length=255, required=False, allow_blank=True)
    is_custom_color = serializers.BooleanField(default=False, required=False)
    custom_color = serializers.CharField(max_length=255, required=False, allow_blank=True)
    is_custom_supplier = serializers.BooleanField(default=False, required=False)
    custom_supplier = serializers.CharField(max_length=255, required=False, allow_blank=True)
    is_custom_related_products = serializers.BooleanField(default=False, required=False)
    custom_related_products = serializers.CharField(max_length=255, required=False, allow_blank=True)

    class Meta:
        model = Product
        fields = [
            'id', 'product_id', 'name', 'product_type', 'description', 'category', 'is_custom_category',
            'custom_category', 'tax_code', 'is_custom_tax_code', 'custom_tax_code', 'unit_price',
            'discount', 'uom', 'is_custom_uom', 'custom_uom', 'quantity', 'stock_level',
            'reorder_level', 'warehouse', 'is_custom_warehouse', 'custom_warehouse', 'size',
            'is_custom_size', 'custom_size', 'color', 'is_custom_color', 'custom_color', 'weight',
            'specifications', 'supplier', 'is_custom_supplier', 'custom_supplier', 'status',
            'product_usage', 'related_products', 'is_custom_related_products', 'custom_related_products',
            'image', 'sub_category',
        ]

    def validate(self, data):
        # Make all non-image fields required, except related_products when is_custom_related_products is true
        required_fields = [
            'name', 'product_type', 'description', 'unit_price', 'discount', 'quantity',
            'stock_level', 'reorder_level', 'weight', 'specifications', 'status',
            'product_usage', 'sub_category'
        ]
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                raise serializers.ValidationError({field: f'{field.replace("_", " ").title()} is required'})

        # Validate dropdown fields
        dropdown_fields = ['category', 'tax_code', 'uom', 'warehouse', 'size', 'color', 'supplier']
        for field in dropdown_fields:
            is_custom = data.get(f'is_custom_{field}', False)
            custom_value = data.get(f'custom_{field}', '')
            field_value = data.get(field)

            if is_custom:
                if not custom_value:
                    raise serializers.ValidationError({
                        f'custom_{field}': f'Custom {field.replace("_", " ").title()} is required when is_custom_{field} is true'
                    })
            else:
                if field_value is None:
                    raise serializers.ValidationError({
                        field: f'{field.replace("_", " ").title()} is required when is_custom_{field} is false'
                    })

        # Validate related_products
        is_custom_related_products = data.get('is_custom_related_products', False)
        custom_related_products = data.get('custom_related_products', '')
        related_products = data.get('related_products', '')

        if is_custom_related_products:
            if not custom_related_products:
                raise serializers.ValidationError({
                    'custom_related_products': 'Custom Related Products is required when is_custom_related_products is true'
                })
        else:
            if not related_products:
                raise serializers.ValidationError({
                    'related_products': 'Related Products is required when is_custom_related_products is false'
                })

        return data

    def create(self, validated_data):
        # Pop custom fields
        custom_fields = {}
        for field in ['category', 'tax_code', 'uom', 'warehouse', 'size', 'color', 'supplier', 'related_products']:
            custom_fields[f'is_custom_{field}'] = validated_data.pop(f'is_custom_{field}', False)
            custom_fields[f'custom_{field}'] = validated_data.pop(f'custom_{field}', '')

        # Create the product
        product = Product.objects.create(**validated_data)

        # Set custom fields
        for field in ['category', 'tax_code', 'uom', 'warehouse', 'size', 'color', 'supplier', 'related_products']:
            if custom_fields[f'is_custom_{field}']:
                setattr(product, f'custom_{field}', custom_fields[f'custom_{field}'])
            else:
                setattr(product, f'custom_{field}', '')

        product.save()
        return product

    def update(self, instance, validated_data):
        # Pop custom fields
        custom_fields = {}
        for field in ['category', 'tax_code', 'uom', 'warehouse', 'size', 'color', 'supplier', 'related_products']:
            custom_fields[f'is_custom_{field}'] = validated_data.pop(f'is_custom_{field}', False)
            custom_fields[f'custom_{field}'] = validated_data.pop(f'custom_{field}', '')

        # Update standard fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update custom fields
        for field in ['category', 'tax_code', 'uom', 'warehouse', 'size', 'color', 'supplier', 'related_products']:
            setattr(instance, f'custom_{field}', custom_fields[f'custom_{field}'] if custom_fields[f'is_custom_{field}'] else '')

        instance.save()
        return instance
    

from .models import Candidate, Department, Role, Branch

from rest_framework import serializers
from .models import Candidate, Department, Role, Branch, CandidateDocument
import re
import logging

logger = logging.getLogger(__name__)

class CandidateDocumentSerializer(serializers.ModelSerializer):
    file = serializers.FileField()

    class Meta:
        model = CandidateDocument
        fields = ['id', 'file', 'uploaded_at']

class CandidateSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), required=False)
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), required=False)
    designation = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), required=False)
    upload_documents = CandidateDocumentSerializer(many=True, required=False)

    class Meta:
        model = Candidate
        fields = [
            'employee_code', 'first_name', 'last_name', 'department', 'branch', 'designation',
            'gender', 'joining_date', 'personal_number', 'emergency_contact_number', 'email',
            'aadhar_number', 'pan_number', 'status', 'current_address', 'highest_qualification',
            'previous_employer', 'total_experience_year', 'total_experience_month',
            'relevant_experience_year', 'relevant_experience_month', 'marital_status',
            'basics', 'hra', 'conveyance_allowance', 'medical_allowance', 'other_allowances',
            'bonus', 'taxes', 'pf', 'esi', 'gross_salary', 'net_salary', 'uan_number',
            'pf_number', 'bank_name', 'account_number', 'ifsc_code', 'asset', 'asset_type',
            'laptop_company_name', 'asset_id', 'upload_documents'
        ]
        depth = 1

    def validate_personal_number(self, value):
        if not value:
            raise serializers.ValidationError("Personal number is required.")
        if not re.match(r'^[0-9+\-\s]+$', value):
            raise serializers.ValidationError("Personal number must contain only digits, +, -, or spaces.")
        return value

    def validate_emergency_contact_number(self, value):
        if value and not re.match(r'^[0-9+\-\s]+$', value):
            raise serializers.ValidationError("Emergency contact number must contain only digits, +, -, or spaces.")
        return value

    def validate_aadhar_number(self, value):
        if not value:
            raise serializers.ValidationError("Aadhar number is required.")
        if not re.match(r'^\d{4}\s?\d{4}\s?\d{4}$', value):
            raise serializers.ValidationError("Aadhar number must be 12 digits, optionally with spaces.")
        return value

    def validate_pan_number(self, value):
        if not value:
            raise serializers.ValidationError("PAN number is required.")
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', value):
            raise serializers.ValidationError("PAN number must be 5 letters, 4 digits, 1 letter (e.g., ABCDE1234F).")
        return value

    def validate_account_number(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError("Account number must contain only digits.")
        return value

    def validate(self, data):
        # Ensure bank details are all provided or none
        bank_fields = ['bank_name', 'account_number', 'ifsc_code']
        provided = [field in data and data[field] for field in bank_fields]
        if any(provided) and not all(provided):
            raise serializers.ValidationError("Bank name, account number, and IFSC code must all be provided or none.")

        # Validate asset-related fields
        asset = data.get('asset', self.instance.asset if self.instance else None)
        if asset == 'Y':
            if not data.get('asset_type'):
                raise serializers.ValidationError("Asset type is required when asset is Yes.")
            if data.get('asset_type') == 'laptop' and not data.get('laptop_company_name'):
                raise serializers.ValidationError("Laptop company name is required when asset type is laptop.")

        logger.info("Validated serializer data: %s", data)
        return data

    def create(self, validated_data):
        upload_documents_data = validated_data.pop('upload_documents', [])
        candidate = super().create(validated_data)
        for document_data in upload_documents_data:
            CandidateDocument.objects.create(candidate=candidate, **document_data)
        return candidate

    def update(self, instance, validated_data):
        upload_documents_data = validated_data.pop('upload_documents', [])
        instance = super().update(instance, validated_data)
        if upload_documents_data:
            instance.upload_documents.all().delete()  # Optional: Replace existing documents
            for document_data in upload_documents_data:
                CandidateDocument.objects.create(candidate=instance, **document_data)
        return instance

from rest_framework import serializers
from .models import Attendance, GovernmentHoliday

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'date', 'check_in_times', 'total_hours']

class CheckInOutSerializer(serializers.Serializer):
    date = serializers.DateField()
    is_check_in = serializers.BooleanField()

class GovernmentHolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = GovernmentHoliday
        fields = ['date', 'description']

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'email']

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Task
        fields = ['id', 'name', 'status', 'start_date', 'due_date', 'assigned_to', 'priority']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['assigned_to'] = {
            'id': instance.assigned_to.id,
            'name': instance.assigned_to.first_name
        }
        return data
    

# serializers.py
from rest_framework import serializers
from .models import Task, Attendance
from .serializers import TaskSerializer, AttendanceSerializer  # Import your existing serializers

class TaskSummarySerializer(serializers.Serializer):
    not_started = serializers.IntegerField()
    in_progress = serializers.IntegerField()
    completed = serializers.IntegerField()
    awaiting_feedback = serializers.IntegerField()

class TaskDataSerializer(serializers.Serializer):
    taskData = TaskSerializer(many=True)
    taskSummary = TaskSummarySerializer()

class DashboardAttendanceSerializer(serializers.Serializer):
    dateData = serializers.ListField(child=serializers.DictField())
    
    
from .models import Customer

from rest_framework import serializers
from .models import Customer, Candidate

class CustomerSerializer(serializers.ModelSerializer):
    assigned_sales_rep = serializers.PrimaryKeyRelatedField(
        queryset=Candidate.objects.filter(designation__role="Sales Representative"),
        allow_null=True
    )
    customer_id = serializers.CharField(required=False, allow_blank=True)  # Not required for input
    available_limit = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)  # Allow empty/null, use default

    class Meta:
        model = Customer
        fields = [
            'id', 'first_name', 'last_name', 'customer_type', 'customer_id',
            'status', 'assigned_sales_rep', 'email', 'phone_number', 'address',
            'street', 'city', 'state', 'zip_code', 'country', 'company_name',
            'industry', 'location', 'gst_tax_id', 'credit_limit', 'available_limit',
            'billing_address', 'shipping_address', 'payment_terms', 'credit_term',
            'last_edit_date'
        ]

    def create(self, validated_data):
        if not validated_data.get('customer_id'):
            validated_data['customer_id'] = self._generate_customer_id()
        if 'available_limit' not in validated_data or validated_data['available_limit'] is None:
            validated_data['available_limit'] = 0.00
        return super().create(validated_data)

    def _generate_customer_id(self):
        last_customer = Customer.objects.order_by('-id').first()
        if last_customer:
            last_id = int(last_customer.customer_id.replace('CUS', '')) + 1
        else:
            last_id = 1
        return f'CUS{last_id:04d}'


 

