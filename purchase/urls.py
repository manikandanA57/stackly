from django.urls import path
from. import views
from .views import PurchaseOrderListView, PurchaseOrderDetailView, PurchaseOrderItemView, PurchaseOrderHistoryView, PurchaseOrderCommentView,  PurchaseOrderEmailView

urlpatterns = [
    path('purchase-orders/', PurchaseOrderListView.as_view(), name='purchase-order-list'),
    path('purchase-orders/<int:pk>/', PurchaseOrderDetailView.as_view(), name='purchase-order-detail'),
    path('purchase-orders/<int:pk>/items/', PurchaseOrderItemView.as_view(), name='purchase-order-items'),
    path('purchase-orders/<int:pk>/history/', PurchaseOrderHistoryView.as_view(), name='purchase-order-history'),
    path('purchase-orders/<int:pk>/comments/', PurchaseOrderCommentView.as_view(), name='purchase-order-comments'),
    # path('purchase-orders/<int:pk>/pdf/', PurchaseOrderPDFView.as_view(), name='purchase-order-pdf'),
    path('purchase-orders/<int:pk>/email/', PurchaseOrderEmailView.as_view(), name='purchase-order-email'),

    path('stock-receipts/', views.StockReceiptListView.as_view(), name='stock-receipt-list'),
    path('stock-receipts/<int:pk>/', views.StockReceiptDetailView.as_view(), name='stock-receipt-detail'),
    path('stock-receipts/<int:pk>/items/', views.StockReceiptItemView.as_view(), name='stock-receipt-items'),
    path('stock-receipts/<int:pk>/pdf/', views.StockReceiptPDFView.as_view(), name='stock-receipt-pdf'),
    path('stock-receipts/<int:pk>/email/', views.StockReceiptEmailView.as_view(), name='stock-receipt-email'),
]