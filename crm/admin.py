from django.contrib import admin
from .models import Enquiry, EnquiryItem, Quotation, QuotationItem, QuotationAttachment, QuotationComment, QuotationHistory, QuotationRevision, SalesOrder, SalesOrderItem, SalesOrderComment, SalesOrderHistory, DeliveryNote, DeliveryNoteItem, DeliveryNoteAttachment, DeliveryNoteRemark, DeliveryNoteCustomerAcknowledgement, Invoice, InvoiceItem, InvoiceAttachment, InvoiceRemark, OrderSummary

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('enquiry_id', 'first_name', 'last_name', 'email', 'enquiry_status', 'priority')
    list_filter = ('enquiry_type', 'enquiry_status', 'priority', 'enquiry_channels')
    search_fields = ('enquiry_id', 'first_name', 'last_name', 'email')
    autocomplete_fields = ['user']

@admin.register(EnquiryItem)
class EnquiryItemAdmin(admin.ModelAdmin):
    list_display = ('item_code', 'product_description', 'enquiry', 'quantity', 'total_amount')
    search_fields = ('item_code', 'product_description')
    autocomplete_fields = ['enquiry']

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ('quotation_id', 'customer_name', 'quotation_type', 'status', 'quotation_date')
    list_filter = ('quotation_type', 'status', 'currency')
    search_fields = ('quotation_id', 'customer_name__first_name', 'customer_name__last_name')
    autocomplete_fields = ['user', 'customer_name', 'sales_rep']

@admin.register(QuotationItem)
class QuotationItemAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'quotation', 'quantity', 'total')
    search_fields = ('product_name',)
    autocomplete_fields = ['quotation', 'product_id', 'uom']

@admin.register(QuotationAttachment)
class QuotationAttachmentAdmin(admin.ModelAdmin):
    list_display = ('file', 'quotation', 'uploaded_by')
    search_fields = ('file',)
    autocomplete_fields = ['quotation', 'uploaded_by']

@admin.register(QuotationComment)
class QuotationCommentAdmin(admin.ModelAdmin):
    list_display = ('quotation', 'person_name', 'comment', 'timestamp')
    search_fields = ('comment',)
    autocomplete_fields = ['quotation', 'person_name']

@admin.register(QuotationHistory)
class QuotationHistoryAdmin(admin.ModelAdmin):
    list_display = ('quotation', 'status', 'action_by', 'timestamp')
    list_filter = ('status',)
    search_fields = ('status',)
    autocomplete_fields = ['quotation', 'action_by']

@admin.register(QuotationRevision)
class QuotationRevisionAdmin(admin.ModelAdmin):
    list_display = ('quotation', 'revision_number', 'status', 'date')
    list_filter = ('status',)
    search_fields = ('quotation__quotation_id',)
    autocomplete_fields = ['quotation', 'created_by']

@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ('sales_order_id', 'customer', 'order_type', 'status', 'order_date')
    list_filter = ('order_type', 'status', 'currency')
    search_fields = ('sales_order_id', 'customer__first_name', 'customer__last_name')
    autocomplete_fields = ['sales_rep', 'customer']

@admin.register(SalesOrderItem)
class SalesOrderItemAdmin(admin.ModelAdmin):
    list_display = ('sales_order', 'product', 'quantity', 'total')
    search_fields = ('product__name',)
    autocomplete_fields = ['sales_order', 'product']

@admin.register(SalesOrderComment)
class SalesOrderCommentAdmin(admin.ModelAdmin):
    list_display = ('sales_order', 'user', 'comment', 'timestamp')
    search_fields = ('comment',)
    autocomplete_fields = ['sales_order', 'user']

@admin.register(SalesOrderHistory)
class SalesOrderHistoryAdmin(admin.ModelAdmin):
    list_display = ('sales_order', 'action', 'user', 'timestamp')
    search_fields = ('action',)
    autocomplete_fields = ['sales_order', 'user']

@admin.register(DeliveryNote)
class DeliveryNoteAdmin(admin.ModelAdmin):
    list_display = ('DN_ID', 'customer_name', 'delivery_type', 'delivery_status', 'delivery_date')
    list_filter = ('delivery_type', 'delivery_status')
    search_fields = ('DN_ID', 'customer_name')
    autocomplete_fields = ['sales_order_reference']

@admin.register(DeliveryNoteItem)
class DeliveryNoteItemAdmin(admin.ModelAdmin):
    list_display = ('delivery_note', 'product', 'quantity')
    search_fields = ('product__name',)
    autocomplete_fields = ['delivery_note', 'product']

@admin.register(DeliveryNoteAttachment)
class DeliveryNoteAttachmentAdmin(admin.ModelAdmin):
    list_display = ('delivery_note', 'file')
    search_fields = ('file',)
    autocomplete_fields = ['delivery_note']

@admin.register(DeliveryNoteRemark)
class DeliveryNoteRemarkAdmin(admin.ModelAdmin):
    list_display = ('delivery_note', 'text', 'created_by', 'timestamp')
    search_fields = ('text',)
    autocomplete_fields = ['delivery_note', 'created_by']

@admin.register(DeliveryNoteCustomerAcknowledgement)
class DeliveryNoteCustomerAcknowledgementAdmin(admin.ModelAdmin):
    list_display = ('delivery_note', 'received_by', 'contact_number')
    search_fields = ('received_by', 'contact_number')
    autocomplete_fields = ['delivery_note']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('INVOICE_ID', 'customer', 'invoice_status', 'payment_status', 'invoice_date')
    list_filter = ('invoice_status', 'payment_status', 'currency')
    search_fields = ('INVOICE_ID', 'customer__first_name', 'customer__last_name')
    autocomplete_fields = ['sales_order_reference', 'customer']

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'product', 'quantity', 'total')
    search_fields = ('product__name',)
    autocomplete_fields = ['invoice', 'product']

@admin.register(InvoiceAttachment)
class InvoiceAttachmentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'file')
    search_fields = ('file',)
    autocomplete_fields = ['invoice']

@admin.register(InvoiceRemark)
class InvoiceRemarkAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'text', 'created_by', 'timestamp')
    search_fields = ('text',)
    autocomplete_fields = ['invoice', 'created_by']

@admin.register(OrderSummary)
class OrderSummaryAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'subtotal', 'grand_total', 'balance_due')
    search_fields = ('invoice__INVOICE_ID',)
    autocomplete_fields = ['invoice']



