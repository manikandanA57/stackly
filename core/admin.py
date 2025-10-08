from django.contrib import admin
from .models import (
    Branch, Department, Role, Profile, Category, TaxCode, UOM, Warehouse, Size, Color,
    Supplier, Product, CandidateDocument, Candidate, GovernmentHoliday, Attendance, Task, Customer
)

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_name', 'code', 'branch')
    list_filter = ('branch',)
    search_fields = ('department_name', 'code')

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role', 'department', 'branch')
    list_filter = ('department', 'branch')
    search_fields = ('role',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'role', 'department', 'branch')
    list_filter = ('role', 'department', 'branch')
    search_fields = ('user__username', 'employee_id')
    autocomplete_fields = ['user', 'role', 'department', 'branch']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(TaxCode)
class TaxCodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'percentage')
    search_fields = ('name',)

@admin.register(UOM)
class UOMAdmin(admin.ModelAdmin):
    list_display = ('name', 'items')
    search_fields = ('name',)

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'manager_name')
    search_fields = ('name', 'location', 'manager_name')

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone_number')
    search_fields = ('name', 'contact_person', 'email')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'name', 'product_type', 'category', 'status', 'stock_level')
    list_filter = ('product_type', 'status', 'category', 'warehouse')
    search_fields = ('product_id', 'name')
    autocomplete_fields = ['category', 'tax_code', 'uom', 'warehouse', 'size', 'color', 'supplier']

@admin.register(CandidateDocument)
class CandidateDocumentAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at')
    search_fields = ('file',)

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('employee_code', 'first_name', 'last_name', 'email', 'department', 'status')
    list_filter = ('department', 'branch', 'status', 'gender')
    search_fields = ('employee_code', 'first_name', 'last_name', 'email')
    autocomplete_fields = ['department', 'branch', 'designation']

@admin.register(GovernmentHoliday)
class GovernmentHolidayAdmin(admin.ModelAdmin):
    list_display = ('date', 'description')
    search_fields = ('description',)
    list_filter = ('date',)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'total_hours')
    list_filter = ('date',)
    search_fields = ('user__username',)
    autocomplete_fields = ['user']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'priority', 'assigned_to', 'due_date')
    list_filter = ('status', 'priority')
    search_fields = ('name', 'assigned_to__username')
    autocomplete_fields = ['assigned_to']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'first_name', 'last_name', 'customer_type', 'status')
    list_filter = ('customer_type', 'status')
    search_fields = ('customer_id', 'first_name', 'last_name', 'email')
    autocomplete_fields = ['assigned_sales_rep']