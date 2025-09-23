
from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Sum, F
from django.db import models
from .models import Supplier, SupplierProduct, Order, SupplierReview
from .serializers import (
    SupplierSerializer, SupplierDetailSerializer, SupplierProductSerializer,
    OrderSerializer, SupplierReviewSerializer, SupplierDashboardSerializer,
    ProductDashboardSerializer, OrderDashboardSerializer
)

class SupplierViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing suppliers"""
    queryset = Supplier.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'region', 'is_verified']
    search_fields = ['name', 'description', 'city', 'address']
    ordering_fields = ['name', 'rating', 'created_at', 'total_orders']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SupplierDetailSerializer
        return SupplierSerializer
    
    def get_permissions(self):
        """Anyone can view suppliers"""
        return [AllowAny()]
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get products for a specific supplier"""
        supplier = self.get_object()
        products = supplier.products.filter(in_stock=True)
        serializer = SupplierProductSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get reviews for a specific supplier"""
        supplier = self.get_object()
        reviews = supplier.reviews.all().order_by('-created_at')
        serializer = SupplierReviewSerializer(reviews, many=True)
        return Response(serializer.data)

class SupplierProductViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing supplier products"""
    queryset = SupplierProduct.objects.filter(in_stock=True)
    serializer_class = SupplierProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['supplier', 'category', 'in_stock']
    search_fields = ['name', 'description', 'category']
    ordering_fields = ['name', 'price', 'created_at']
    
    def get_permissions(self):
        """Anyone can view products"""
        return [AllowAny()]

class OrderViewSet(viewsets.ModelViewSet):
    """API endpoint for managing orders"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only show user's own orders"""
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order"""
        order = self.get_object()
        
        # Only pending or confirmed orders can be cancelled
        if order.status not in ['pending', 'confirmed']:
            return Response(
                {"detail": "Only pending or confirmed orders can be cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'cancelled'
        order.save()
        
        return Response({"detail": "Order cancelled successfully."})

class SupplierReviewViewSet(viewsets.ModelViewSet):
    """API endpoint for managing supplier reviews"""
    serializer_class = SupplierReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SupplierReview.objects.filter(user=self.request.user)

# Supplier Dashboard Views
class SupplierDashboardViewSet(viewsets.ModelViewSet):
    """API endpoint for supplier dashboard management"""
    serializer_class = SupplierDashboardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only show supplier that belongs to the authenticated user"""
        return Supplier.objects.filter(dashboard_user=self.request.user)
    
    def perform_create(self, serializer):
        """Associate supplier with the authenticated user"""
        serializer.save(dashboard_user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def dashboard_stats(self, request, pk=None):
        """Get dashboard statistics for supplier"""
        supplier = self.get_object()
        
        stats = {
            'total_products': supplier.products.count(),
            'active_products': supplier.products.filter(in_stock=True).count(),
            'low_stock_products': supplier.products.filter(
                stock_quantity__lte=F('low_stock_threshold')
            ).count(),
            'total_orders': supplier.orders.count(),
            'pending_orders': supplier.orders.filter(status='pending').count(),
            'delivered_orders': supplier.orders.filter(status='delivered').count(),
            'total_revenue': supplier.orders.filter(status='delivered').aggregate(
                total=Sum('total')
            )['total'] or 0,
            'average_rating': supplier.reviews.aggregate(
                avg=Avg('rating')
            )['avg'] or 0,
            'total_reviews': supplier.reviews.count(),
        }
        
        return Response(stats)

class ProductDashboardViewSet(viewsets.ModelViewSet):
    """API endpoint for managing products in supplier dashboard"""
    serializer_class = ProductDashboardSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'in_stock', 'featured']
    search_fields = ['name', 'description', 'brand', 'tags']
    ordering_fields = ['name', 'price', 'stock_quantity', 'created_at']
    
    def get_queryset(self):
        """Only show products for the supplier owned by authenticated user"""
        if hasattr(self.request.user, 'supplier_dashboard'):
            return SupplierProduct.objects.filter(supplier=self.request.user.supplier_dashboard)
        return SupplierProduct.objects.none()
    
    def perform_create(self, serializer):
        """Associate product with user's supplier"""
        if hasattr(self.request.user, 'supplier_dashboard'):
            serializer.save(supplier=self.request.user.supplier_dashboard)
        else:
            raise serializers.ValidationError("User does not have a supplier dashboard.")
    
    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """Update product stock quantity"""
        product = self.get_object()
        new_quantity = request.data.get('stock_quantity')
        
        if new_quantity is None:
            return Response(
                {"detail": "stock_quantity is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product.stock_quantity = float(new_quantity)
            product.in_stock = product.stock_quantity > 0
            product.save()
            
            serializer = self.get_serializer(product)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {"detail": "Invalid stock quantity"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def toggle_stock_status(self, request, pk=None):
        """Toggle product in_stock status"""
        product = self.get_object()
        product.in_stock = not product.in_stock
        product.save()
        
        serializer = self.get_serializer(product)
        return Response(serializer.data)

class OrderDashboardViewSet(viewsets.ModelViewSet):
    """API endpoint for managing orders in supplier dashboard"""
    serializer_class = OrderDashboardSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'total']
    
    def get_queryset(self):
        """Only show orders for the supplier owned by authenticated user"""
        if hasattr(self.request.user, 'supplier_dashboard'):
            return Order.objects.filter(supplier=self.request.user.supplier_dashboard).order_by('-created_at')
        return Order.objects.none()
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update order status"""
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response(
                {"detail": "Invalid status"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        order.save()
        
        # Update supplier total orders if delivered
        if new_status == 'delivered':
            supplier = order.supplier
            supplier.total_orders += 1
            supplier.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)

# Additional API endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supplier_dashboard_overview(request):
    """Get overview data for supplier dashboard"""
    try:
        supplier = request.user.supplier_dashboard
    except Supplier.DoesNotExist:
        return Response(
            {"detail": "User does not have a supplier dashboard"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get recent orders
    recent_orders = supplier.orders.order_by('-created_at')[:5]
    
    # Get low stock products
    low_stock_products = supplier.products.filter(
        stock_quantity__lte=F('low_stock_threshold')
    )[:5]
    
    # Get top selling products (based on order items)
    top_products = supplier.products.annotate(
        total_sold=Count('orderitem')
    ).order_by('-total_sold')[:5]
    
    data = {
        'supplier': SupplierDashboardSerializer(supplier).data,
        'recent_orders': OrderDashboardSerializer(recent_orders, many=True).data,
        'low_stock_products': ProductDashboardSerializer(low_stock_products, many=True).data,
        'top_products': ProductDashboardSerializer(top_products, many=True).data,
    }
    
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_supplier_account(request):
    """Create a supplier account for the authenticated user"""
    if hasattr(request.user, 'supplier_dashboard'):
        return Response(
            {"detail": "User already has a supplier account"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = SupplierDashboardSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(dashboard_user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_supplier(request):
    """Public endpoint for suppliers to register (no authentication required)"""
    serializer = SupplierSerializer(data=request.data)
    if serializer.is_valid():
        # Create supplier without dashboard_user initially
        supplier = serializer.save(is_verified=False, is_active=True)
        return Response({
            "detail": "Supplier registered successfully. Please contact admin for verification.",
            "supplier": serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_supplier(request, supplier_id):
    """Admin endpoint to verify a supplier"""
    try:
        supplier = Supplier.objects.get(id=supplier_id)
        supplier.is_verified = True
        supplier.save()
        return Response({
            "detail": "Supplier verified successfully",
            "supplier": SupplierSerializer(supplier).data
        })
    except Supplier.DoesNotExist:
        return Response(
            {"detail": "Supplier not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_supplier_active(request, supplier_id):
    """Admin endpoint to toggle supplier active status"""
    try:
        supplier = Supplier.objects.get(id=supplier_id)
        supplier.is_active = not supplier.is_active
        supplier.save()
        return Response({
            "detail": f"Supplier {'activated' if supplier.is_active else 'deactivated'} successfully",
            "supplier": SupplierSerializer(supplier).data
        })
    except Supplier.DoesNotExist:
        return Response(
            {"detail": "Supplier not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )

