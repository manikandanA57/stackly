# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import PurchaseOrder, PurchaseOrderItem, PurchaseOrderHistory, PurchaseOrderComment
from .serializers import PurchaseOrderSerializer, PurchaseOrderItemSerializer, PurchaseOrderHistorySerializer, PurchaseOrderCommentSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from reportlab.lib import colors
# from reportlab.lib.pagesizes = letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import io

class PurchaseOrderListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        purchase_orders = PurchaseOrder.objects.all().order_by('-PO_date')
        serializer = PurchaseOrderSerializer(purchase_orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PurchaseOrderSerializer(data=request.data)
        if serializer.is_valid():
            purchase_order = serializer.save()
            return Response(PurchaseOrderSerializer(purchase_order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PurchaseOrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            purchase_order = PurchaseOrder.objects.get(id=pk)
            serializer = PurchaseOrderSerializer(purchase_order)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'error': 'Purchase Order not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            purchase_order = PurchaseOrder.objects.get(id=pk)
            action = request.data.get('action')
            if action == 'submit_draft':
                purchase_order.status = 'Submitted'
            elif action == 'cancel':
                purchase_order.status = 'Canceled'
            else:
                serializer = PurchaseOrderSerializer(purchase_order, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(PurchaseOrderSerializer(purchase_order).data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            purchase_order.save()
            PurchaseOrderHistory.objects.create(purchase_order=purchase_order, action=action, performed_by=request.user.username)
            return Response(PurchaseOrderSerializer(purchase_order).data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': 'Purchase Order not found'}, status=status.HTTP_404_NOT_FOUND)

class PurchaseOrderItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            purchase_order = PurchaseOrder.objects.get(id=pk)
            item_data = request.data
            item_data['purchase_order'] = pk
            serializer = PurchaseOrderItemSerializer(data=item_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({'error': 'Purchase Order not found'}, status=status.HTTP_404_NOT_FOUND)

class PurchaseOrderHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            purchase_order = PurchaseOrder.objects.get(id=pk)
            history = purchase_order.history.all()
            serializer = PurchaseOrderHistorySerializer(history, many=True)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'error': 'Purchase Order not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, pk):
        try:
            purchase_order = PurchaseOrder.objects.get(id=pk)
            history_data = request.data
            history_data['purchase_order'] = pk
            serializer = PurchaseOrderHistorySerializer(data=history_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({'error': 'Purchase Order not found'}, status=status.HTTP_404_NOT_FOUND)

class PurchaseOrderCommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            purchase_order = PurchaseOrder.objects.get(id=pk)
            comments = purchase_order.comments.all()
            serializer = PurchaseOrderCommentSerializer(comments, many=True)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'error': 'Purchase Order not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, pk):
        try:
            purchase_order = PurchaseOrder.objects.get(id=pk)
            comment_data = request.data
            comment_data['purchase_order'] = pk
            serializer = PurchaseOrderCommentSerializer(data=comment_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({'error': 'Purchase Order not found'}, status=status.HTTP_404_NOT_FOUND)

# class PurchaseOrderPDFView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, pk):
#         try:
#             purchase_order = PurchaseOrder.objects.get(id=pk)
#             buffer = io.BytesIO()
#             doc = SimpleDocTemplate(buffer, pagesize=letter)
#             elements = []

#             data = [
#                 ['PO ID', purchase_order.PO_ID],
#                 ['PO Date', purchase_order.PO_date],
#                 ['Supplier', purchase_order.supplier_name],
#                 ['Total', purchase_order.total_order_value],
#             ]
#             table = Table(data)
#             table.setStyle(TableStyle([
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, 0), 14),
#                 ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                 ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#                 ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
#                 ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
#                 ('FONTSIZE', (0, 1), (-1, -1), 12),
#             ]))
#             elements.append(table)

#             doc.build(elements)
#             buffer.seek(0)
#             response = HttpResponse(buffer, content_type='application/pdf')
#             response['Content-Disposition'] = f'attachment; filename="purchase_order_{purchase_order.PO_ID}.pdf"'
#             return response
#         except ObjectDoesNotExist:
#             return Response({'error': 'Purchase Order not found'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PurchaseOrderEmailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            purchase_order = PurchaseOrder.objects.get(id=pk)
            email = request.data.get('email')
            if not email:
                return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

            subject = f'Purchase Order {purchase_order.PO_ID}'
            html_message = render_to_string('purchase_order_email_template.html', {'purchase_order': purchase_order})
            msg = EmailMessage(subject, html_message, to=[email])
            msg.content_subtype = 'html'
            msg.send()
            return Response({'message': 'Email sent successfully'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': 'Purchase Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import StockReceipt, StockReceiptItem, SerialNumber, BatchNumber, BatchSerialNumber, StockReceiptRemark, StockReceiptAttachment
from .serializers import StockReceiptSerializer, StockReceiptItemSerializer, SerialNumberSerializer, BatchNumberSerializer, StockReceiptAttachmentSerializer, StockReceiptRemarkSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import io

class StockReceiptListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        stock_receipts = StockReceipt.objects.all().order_by('-received_date')
        serializer = StockReceiptSerializer(stock_receipts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StockReceiptSerializer(data=request.data)
        if serializer.is_valid():
            stock_receipt = serializer.save()
            return Response(StockReceiptSerializer(stock_receipt).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StockReceiptDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            stock_receipt = StockReceipt.objects.get(id=pk)
            serializer = StockReceiptSerializer(stock_receipt)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'error': 'Stock Receipt not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            stock_receipt = StockReceipt.objects.get(id=pk)
            action = request.data.get('action')
            if action == 'cancel':
                stock_receipt.status = 'Cancelled'
            else:
                serializer = StockReceiptSerializer(stock_receipt, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(StockReceiptSerializer(stock_receipt).data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            stock_receipt.save()
            return Response(StockReceiptSerializer(stock_receipt).data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': 'Stock Receipt not found'}, status=status.HTTP_404_NOT_FOUND)

class StockReceiptItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            stock_receipt = StockReceipt.objects.get(id=pk)
            item_data = request.data
            item_data['stock_receipt'] = pk
            serializer = StockReceiptItemSerializer(data=item_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({'error': 'Stock Receipt not found'}, status=status.HTTP_404_NOT_FOUND)

class StockReceiptPDFView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            stock_receipt = StockReceipt.objects.get(id=pk)
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []

            data = [
                ['GRN ID', stock_receipt.GRN_ID],
                ['Received Date', stock_receipt.received_date],
                ['Supplier', stock_receipt.supplier.name],
                ['Total Items', len(stock_receipt.items.all())],
            ]
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
            ]))
            elements.append(table)

            doc.build(elements)
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="stock_receipt_{stock_receipt.GRN_ID}.pdf"'
            return response
        except ObjectDoesNotExist:
            return Response({'error': 'Stock Receipt not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StockReceiptEmailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            stock_receipt = StockReceipt.objects.get(id=pk)
            email = request.data.get('email')
            if not email:
                return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

            subject = f'Stock Receipt {stock_receipt.GRN_ID}'
            html_message = render_to_string('stock_receipt_email_template.html', {'stock_receipt': stock_receipt})
            msg = EmailMessage(subject, html_message, to=[email])
            msg.content_subtype = 'html'
            msg.send()
            return Response({'message': 'Email sent successfully'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': 'Stock Receipt not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)