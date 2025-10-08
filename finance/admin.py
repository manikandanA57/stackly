from django.contrib import admin
from .models import (
    CreditNote, CreditNoteItem, CreditNoteAttachment, CreditNoteRemark, CreditNotePaymentRefund,
    DebitNote, DebitNoteItem, DebitNoteAttachment, DebitNoteRemark, DebitNotePaymentRecover
)

from .models import CreditNote
from crm.models import Customer

@admin.register(CreditNote)
class CreditNoteAdmin(admin.ModelAdmin):
    list_display = ('CREDIT_NOTE_ID', 'customer', 'invoice_status', 'payment_status', 'credit_note_date')
    list_filter = ('invoice_status', 'payment_status', 'currency')
    search_fields = ('CREDIT_NOTE_ID', 'customer__first_name', 'customer__last_name')
    autocomplete_fields = ['invoice_reference', 'created_by', 'branch', 'customer']

@admin.register(CreditNoteItem)
class CreditNoteItemAdmin(admin.ModelAdmin):
    list_display = ('credit_note', 'product', 'returned_qty', 'total')
    search_fields = ('product__name',)
    autocomplete_fields = ['credit_note', 'product']

@admin.register(CreditNoteAttachment)
class CreditNoteAttachmentAdmin(admin.ModelAdmin):
    list_display = ('credit_note', 'file')
    search_fields = ('file',)
    autocomplete_fields = ['credit_note']

@admin.register(CreditNoteRemark)
class CreditNoteRemarkAdmin(admin.ModelAdmin):
    list_display = ('credit_note', 'text', 'created_by', 'timestamp')
    search_fields = ('text',)
    autocomplete_fields = ['credit_note', 'created_by']

@admin.register(CreditNotePaymentRefund)
class CreditNotePaymentRefundAdmin(admin.ModelAdmin):
    list_display = ('credit_note', 'amount_paid_by_customer', 'balance_to_refund', 'refund_mode')
    search_fields = ('credit_note__CREDIT_NOTE_ID',)
    autocomplete_fields = ['credit_note']

@admin.register(DebitNote)
class DebitNoteAdmin(admin.ModelAdmin):
    list_display = ('DEBIT_NOTE_ID', 'supplier', 'payment_status', 'debit_note_date')
    list_filter = ('payment_status', 'currency')
    search_fields = ('DEBIT_NOTE_ID', 'supplier__name')
    autocomplete_fields = ['po_reference', 'created_by', 'branch', 'supplier']

@admin.register(DebitNoteItem)
class DebitNoteItemAdmin(admin.ModelAdmin):
    list_display = ('debit_note', 'product', 'returned_qty', 'total')
    search_fields = ('product__name',)
    autocomplete_fields = ['debit_note', 'product']

@admin.register(DebitNoteAttachment)
class DebitNoteAttachmentAdmin(admin.ModelAdmin):
    list_display = ('debit_note', 'file')
    search_fields = ('file',)
    autocomplete_fields = ['debit_note']

@admin.register(DebitNoteRemark)
class DebitNoteRemarkAdmin(admin.ModelAdmin):
    list_display = ('debit_note', 'text', 'created_by', 'timestamp')
    search_fields = ('text',)
    autocomplete_fields = ['debit_note', 'created_by']

@admin.register(DebitNotePaymentRecover)
class DebitNotePaymentRecoverAdmin(admin.ModelAdmin):
    list_display = ('debit_note', 'amount_paid_to_vendor', 'balance_to_recover', 'refund_mode')
    search_fields = ('debit_note__DEBIT_NOTE_ID',)
    autocomplete_fields = ['debit_note']
from django.contrib import admin
from .models import Customer

 
