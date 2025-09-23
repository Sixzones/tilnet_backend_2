
from rest_framework import serializers
from .models import Supplier, SupplierProduct, Order, OrderItem, SupplierReview

class SupplierProductSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    discounted_price = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = SupplierProduct
        fields = '__all__'

class SupplierSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    active_products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Supplier
        fields = '__all__'
    
    def get_products_count(self, obj):
        return obj.products.count()
    
    def get_active_products_count(self, obj):
        return obj.products.filter(in_stock=True).count()

class SupplierDetailSerializer(serializers.ModelSerializer):
    products = SupplierProductSerializer(many=True, read_only=True)
    
    class Meta:
        model = Supplier
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'unit_price', 'total_price')
        read_only_fields = ('total_price',)

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('user', 'subtotal', 'total', 'status', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Calculate subtotal and total
        subtotal = 0
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            unit_price = product.price
            subtotal += quantity * unit_price
        
        delivery_fee = validated_data.get('delivery_fee', 0)
        total = subtotal + delivery_fee
        
        # Create order
        validated_data['user'] = self.context['request'].user
        validated_data['subtotal'] = subtotal
        validated_data['total'] = total
        
        order = Order.objects.create(**validated_data)
        
        # Create order items
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            unit_price = product.price
            total_price = quantity * unit_price
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price
            )
        
        return order

class SupplierReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = SupplierReview
        fields = '__all__'
        read_only_fields = ('user', 'created_at')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

# Dashboard Serializers for Supplier Management
class SupplierDashboardSerializer(serializers.ModelSerializer):
    """Serializer for supplier dashboard operations"""
    products_count = serializers.SerializerMethodField()
    active_products_count = serializers.SerializerMethodField()
    pending_orders_count = serializers.SerializerMethodField()
    total_revenue = serializers.SerializerMethodField()
    
    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ('dashboard_user', 'rating', 'total_orders', 'created_at', 'updated_at')
    
    def get_products_count(self, obj):
        return obj.products.count()
    
    def get_active_products_count(self, obj):
        return obj.products.filter(in_stock=True).count()
    
    def get_pending_orders_count(self, obj):
        return obj.orders.filter(status__in=['pending', 'confirmed']).count()
    
    def get_total_revenue(self, obj):
        completed_orders = obj.orders.filter(status='delivered')
        return sum(order.total for order in completed_orders)

class ProductDashboardSerializer(serializers.ModelSerializer):
    """Serializer for product management in dashboard"""
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    discounted_price = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = SupplierProduct
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def validate_supplier(self, value):
        """Ensure user can only manage their own supplier's products"""
        request = self.context.get('request')
        if request and hasattr(request.user, 'supplier_dashboard'):
            if value != request.user.supplier_dashboard:
                raise serializers.ValidationError("You can only manage your own supplier's products.")
        return value

class OrderDashboardSerializer(serializers.ModelSerializer):
    """Serializer for order management in dashboard"""
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='user.full_name', read_only=True)
    customer_phone = serializers.CharField(source='user.phone_number', read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('user', 'subtotal', 'total', 'created_at', 'updated_at')
