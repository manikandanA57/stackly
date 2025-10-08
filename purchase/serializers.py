from rest_framework import serializers
from .models import PurchaseOrder, PurchaseOrderItem, PurchaseOrderHistory, PurchaseOrderComment

class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        fields = ['id', 'product', 'qty_ordered', 'insufficient_stock', 'unit_price', 'tax', 'discount', 'total']
        read_only_fields = ['total', 'purchase_order']

class PurchaseOrderHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderHistory
        fields = ['id', 'action', 'performed_by', 'timestamp', 'details']
        read_only_fields = ['purchase_order']

class PurchaseOrderCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderComment
        fields = ['id', 'comment', 'created_by', 'timestamp']
        read_only_fields = ['purchase_order']

class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True, required=False)
    history = PurchaseOrderHistorySerializer(many=True, required=False)
    comments = PurchaseOrderCommentSerializer(many=True, required=False)

    class Meta:
        model = PurchaseOrder
        fields = ['id', 'PO_ID', 'PO_date', 'delivery_date', 'status', 'sales_order_reference', 'supplier', 'supplier_name', 'payment_terms', 'inco_terms', 'currency', 'notes_comments', 'subtotal', 'global_discount', 'tax_summary', 'shipping_charges', 'rounding_adjustment', 'total_order_value', 'upload_file_path', 'items', 'history', 'comments']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        history_data = validated_data.pop('history', [])
        comments_data = validated_data.pop('comments', [])
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        for item_data in items_data:
            PurchaseOrderItem.objects.create(purchase_order=purchase_order, **item_data)
        for history_entry in history_data:
            PurchaseOrderHistory.objects.create(purchase_order=purchase_order, **history_entry)
        for comment_data in comments_data:
            PurchaseOrderComment.objects.create(purchase_order=purchase_order, **comment_data)
        return purchase_order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])
        history_data = validated_data.pop('history', [])
        comments_data = validated_data.pop('comments', [])
        instance = super().update(instance, validated_data)
        if items_data:
            instance.items.all().delete()
            for item_data in items_data:
                PurchaseOrderItem.objects.create(purchase_order=instance, **item_data)
        if history_data:
            instance.history.all().delete()
            for history_entry in history_data:
                PurchaseOrderHistory.objects.create(purchase_order=instance, **history_entry)
        if comments_data:
            instance.comments.all().delete()
            for comment_data in comments_data:
                PurchaseOrderComment.objects.create(purchase_order=instance, **comment_data)
        return instance
    

from rest_framework import serializers
from .models import StockReceipt, StockReceiptItem, SerialNumber, BatchNumber, BatchSerialNumber, StockReceiptRemark, StockReceiptAttachment

class StockReceiptAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockReceiptAttachment
        fields = ['id', 'file']

class StockReceiptRemarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockReceiptRemark
        fields = ['id', 'text', 'created_by', 'timestamp']

class SerialNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = SerialNumber
        fields = ['id', 'serial_no']

class BatchSerialNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchSerialNumber
        fields = ['id', 'serial_no']

class BatchNumberSerializer(serializers.ModelSerializer):
    serial_numbers = BatchSerialNumberSerializer(many=True, required=False)

    class Meta:
        model = BatchNumber
        fields = ['id', 'batch_no', 'batch_qty', 'mfg_date', 'expiry_date', 'serial_numbers']

    def create(self, validated_data):
        serial_numbers_data = validated_data.pop('serial_numbers', [])
        batch = BatchNumber.objects.create(**validated_data)
        for serial_data in serial_numbers_data:
            BatchSerialNumber.objects.create(batch_number=batch, **serial_data)
        return batch

class StockReceiptItemSerializer(serializers.ModelSerializer):
    serial_numbers = SerialNumberSerializer(many=True, required=False)
    batch_numbers = BatchNumberSerializer(many=True, required=False)

    class Meta:
        model = StockReceiptItem
        fields = ['id', 'product', 'product_id', 'uom', 'qty_ordered', 'qty_received', 'accepted_qty', 'rejected_qty', 'qty_returned', 'stock_dim', 'warehouse', 'serial_numbers', 'batch_numbers']
        extra_kwargs = {
            'product_id': {'required': False, 'allow_blank': True},
            'uom': {'required': False, 'allow_blank': True},
            'qty_ordered': {'required': False, 'allow_null': True},
        }

    def create(self, validated_data):
        serial_numbers_data = validated_data.pop('serial_numbers', [])
        batch_numbers_data = validated_data.pop('batch_numbers', [])
        item = StockReceiptItem.objects.create(**validated_data)
        for serial_data in serial_numbers_data:
            SerialNumber.objects.create(stock_receipt_item=item, **serial_data)
        for batch_data in batch_numbers_data:
            BatchNumberSerializer().create(batch_data)
        return item

class StockReceiptSerializer(serializers.ModelSerializer):
    items = StockReceiptItemSerializer(many=True, required=False)
    attachments = StockReceiptAttachmentSerializer(many=True, required=False)
    remarks = StockReceiptRemarkSerializer(many=True, required=False)

    class Meta:
        model = StockReceipt
        fields = ['id', 'GRN_ID', 'PO_reference', 'received_date', 'supplier', 'supplier_dn_no', 'supplier_invoice_no', 'received_by', 'qc_done_by', 'status', 'remarks', 'attachments', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        attachments_data = validated_data.pop('attachments', [])
        remarks_data = validated_data.pop('remarks', [])
        stock_receipt = StockReceipt.objects.create(**validated_data)
        for item_data in items_data:
            StockReceiptItemSerializer().create(item_data)
        for attachment_data in attachments_data:
            StockReceiptAttachment.objects.create(stock_receipt=stock_receipt, **attachment_data)
        for remark_data in remarks_data:
            StockReceiptRemark.objects.create(stock_receipt=stock_receipt, **remark_data)
        return stock_receipt

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])
        attachments_data = validated_data.pop('attachments', [])
        remarks_data = validated_data.pop('remarks', [])
        instance = super().update(instance, validated_data)
        if items_data:
            instance.items.all().delete()
            for item_data in items_data:
                StockReceiptItemSerializer().create(item_data)
        if attachments_data:
            instance.attachments.all().delete()
            for attachment_data in attachments_data:
                StockReceiptAttachment.objects.create(stock_receipt=instance, **attachment_data)
        if remarks_data:
            instance.remarks.all().delete()
            for remark_data in remarks_data:
                StockReceiptRemark.objects.create(stock_receipt=instance, **remark_data)
        return instance