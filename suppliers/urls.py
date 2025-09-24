
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# Public endpoints (for customers)
router.register(r'suppliers', views.SupplierViewSet, basename='supplier')
router.register(r'products', views.SupplierProductViewSet, basename='supplier-product')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'reviews', views.SupplierReviewViewSet, basename='supplier-review')

# Dashboard endpoints (for suppliers)
router.register(r'dashboard/supplier', views.SupplierDashboardViewSet, basename='supplier-dashboard')
router.register(r'dashboard/products', views.ProductDashboardViewSet, basename='product-dashboard')
router.register(r'dashboard/orders', views.OrderDashboardViewSet, basename='order-dashboard')

urlpatterns = [
    path('', include(router.urls)),
    # Additional dashboard endpoints
    path('dashboard/overview/', views.supplier_dashboard_overview, name='supplier-dashboard-overview'),
    path('dashboard/create-account/', views.create_supplier_account, name='create-supplier-account'),
    # Public supplier registration
    path('register/', views.register_supplier, name='register-supplier'),
    # Admin endpoints
    path('admin/verify/<int:supplier_id>/', views.verify_supplier, name='verify-supplier'),
    path('admin/toggle-active/<int:supplier_id>/', views.toggle_supplier_active, name='toggle-supplier-active'),
]
