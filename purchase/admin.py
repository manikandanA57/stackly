from django.contrib import admin
from .models import (
    PurchaseOrder, PurchaseOrderItem, PurchaseOrderHistory, PurchaseOrderComment,
    StockReceipt, StockReceiptItem, StockReceiptAttachment, StockReceiptRemark,
    SerialNumber, BatchNumber, BatchSerialNumber, StockReturn, StockReturnItem,
    StockReturnAttachment, StockReturnRemark, SerialNumberReturn
)

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('PO_ID', 'supplier', 'status', 'PO_date', 'total_order_value')
    list_filter = ('status', 'currency')
    search_fields = ('PO_ID', 'supplier__name')
    autocomplete_fields = ['supplier']

@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ('purchase_order', 'product', 'qty_ordered', 'total')
    search_fields = ('product__name',)
    autocomplete_fields = ['purchase_order', 'product']

@admin.register(PurchaseOrderHistory)
class PurchaseOrderHistoryAdmin(admin.ModelAdmin):
    list_display = ('purchase_order', 'action', 'performed_by', 'timestamp')
    search_fields = ('action', 'performed_by')
    autocomplete_fields = ['purchase_order']

@admin.register(PurchaseOrderComment)
class PurchaseOrderCommentAdmin(admin.ModelAdmin):
    list_display = ('purchase_order', 'comment', 'created_by', 'timestamp')
    search_fields = ('comment', 'created_by')
    autocomplete_fields = ['purchase_order']

@admin.register(StockReceipt)
class StockReceiptAdmin(admin.ModelAdmin):
    list_display = ('GRN_ID', 'supplier', 'status', 'received_date')
    list_filter = ('status',)
    search_fields = ('GRN_ID', 'supplier__name')
    autocomplete_fields = ['PO_reference', 'supplier', 'received_by', 'qc_done_by']

@admin.register(StockReceiptItem)
class StockReceiptItemAdmin(admin.ModelAdmin):
    list_display = ('stock_receipt', 'product', 'qty_received', 'accepted_qty', 'total')
    search_fields = ('product__name',)
    autocomplete_fields = ['stock_receipt', 'product', 'warehouse']

@admin.register(StockReceiptAttachment)
class StockReceiptAttachmentAdmin(admin.ModelAdmin):
    list_display = ('stock_receipt', 'file')
    search_fields = ('file',)
    autocomplete_fields = ['stock_receipt']

@admin.register(StockReceiptRemark)
class StockReceiptRemarkAdmin(admin.ModelAdmin):
    list_display = ('stock_receipt', 'text', 'created_by', 'timestamp')
    search_fields = ('text',)
    autocomplete_fields = ['stock_receipt', 'created_by']

@admin.register(SerialNumber)
class SerialNumberAdmin(admin.ModelAdmin):
    list_display = ('stock_receipt_item', 'serial_no')
    search_fields = ('serial_no',)
    autocomplete_fields = ['stock_receipt_item']

@admin.register(BatchNumber)
class BatchNumberAdmin(admin.ModelAdmin):
    list_display = ('stock_receipt_item', 'batch_no', 'batch_qty', 'mfg_date', 'expiry_date')
    search_fields = ('batch_no',)
    autocomplete_fields = ['stock_receipt_item']

@admin.register(BatchSerialNumber)
class BatchSerialNumberAdmin(admin.ModelAdmin):
    list_display = ('batch_number', 'serial_no')
    search_fields = ('serial_no',)
    autocomplete_fields = ['batch_number']

@admin.register(StockReturn)
class StockReturnAdmin(admin.ModelAdmin):
    list_display = ('SRN_ID', 'supplier', 'status', 'return_date', 'amount_to_recover')
    list_filter = ('status',)
    search_fields = ('SRN_ID', 'supplier__name')
    autocomplete_fields = ['PO_reference', 'GRN_reference', 'supplier', 'return_initiated_by']

@admin.register(StockReturnItem)
class StockReturnItemAdmin(admin.ModelAdmin):
    list_display = ('stock_return', 'product', 'qty_returned', 'total')
    search_fields = ('product__name',)
    autocomplete_fields = ['stock_return', 'stock_receipt_item', 'product']

@admin.register(StockReturnAttachment)
class StockReturnAttachmentAdmin(admin.ModelAdmin):
    list_display = ('stock_return', 'file')
    search_fields = ('file',)
    autocomplete_fields = ['stock_return']

@admin.register(StockReturnRemark)
class StockReturnRemarkAdmin(admin.ModelAdmin):
    list_display = ('stock_return', 'text', 'created_by', 'timestamp')
    search_fields = ('text',)
    autocomplete_fields = ['stock_return', 'created_by']

@admin.register(SerialNumberReturn)
class SerialNumberReturnAdmin(admin.ModelAdmin):
    list_display = ('stock_return_item', 'serial_no')
    search_fields = ('serial_no',)
    autocomplete_fields = ['stock_return_item']
