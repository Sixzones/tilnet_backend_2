
from django.db import models
from django.conf import settings

class Supplier(models.Model):
    """Model for material suppliers"""
    # Basic Information
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='supplier_logos/', null=True, blank=True)
    shop_image = models.ImageField(upload_to='supplier_shops/', null=True, blank=True)
    
    # Contact Information
    address = models.TextField()
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20)
    whatsapp = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    # Business Information
    business_registration = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=100, blank=True)
    years_in_business = models.IntegerField(default=0)
    
    # Operational Details
    opening_hours = models.CharField(max_length=255, blank=True, help_text="e.g., Mon-Fri: 8AM-6PM, Sat: 8AM-4PM")
    delivery_areas = models.TextField(blank=True, help_text="Areas where supplier delivers")
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status and Ratings
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    total_orders = models.IntegerField(default=0)
    
    # Dashboard Access
    dashboard_user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='supplier_dashboard'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-rating', 'name']
    
    def __str__(self):
        return self.name
    
    def update_rating(self):
        """Update supplier rating based on reviews"""
        reviews = self.reviews.all()
        if reviews.exists():
            avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.rating = round(avg_rating, 1) if avg_rating else 0
            self.save()

class SupplierProduct(models.Model):
    """Products offered by suppliers"""
    CATEGORY_CHOICES = [
        ('tiles', 'Tiles'),
        ('cement', 'Cement'),
        ('sand', 'Sand'),
        ('grout', 'Grout'),
        ('adhesive', 'Adhesive'),
        ('tools', 'Tools'),
        ('hardware', 'Hardware'),
        ('other', 'Other'),
    ]
    
    UNIT_CHOICES = [
        ('piece', 'Piece'),
        ('box', 'Box'),
        ('bag', 'Bag'),
        ('ton', 'Ton'),
        ('cubic_meter', 'Cubic Meter'),
        ('square_meter', 'Square Meter'),
        ('liter', 'Liter'),
        ('kilogram', 'Kilogram'),
    ]
    
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='supplier_products/', null=True, blank=True)
    
    # Additional product images
    image2 = models.ImageField(upload_to='supplier_products/', null=True, blank=True)
    image3 = models.ImageField(upload_to='supplier_products/', null=True, blank=True)
    
    unit = models.CharField(max_length=50, choices=UNIT_CHOICES)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    
    # Stock Management
    in_stock = models.BooleanField(default=True)
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    low_stock_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=10)
    
    # Product Details
    brand = models.CharField(max_length=100, blank=True)
    model_number = models.CharField(max_length=100, blank=True)
    specifications = models.TextField(blank=True)
    
    # Pricing
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # SEO and Marketing
    featured = models.BooleanField(default=False)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-featured', '-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.supplier.name}"
    
    @property
    def discounted_price(self):
        """Calculate price after discount"""
        if self.discount_percentage > 0:
            discount_amount = (self.price * self.discount_percentage) / 100
            return self.price - discount_amount
        return self.price
    
    @property
    def is_low_stock(self):
        """Check if product is low on stock"""
        return self.stock_quantity <= self.low_stock_threshold

class Order(models.Model):
    """Customer orders from suppliers"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    delivery_address = models.TextField()
    delivery_instructions = models.TextField(blank=True)
    contact_phone = models.CharField(max_length=20)
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    
    payment_method = models.CharField(max_length=50, blank=True)
    payment_reference = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.status}"

class OrderItem(models.Model):
    """Items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(SupplierProduct, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity} - Order #{self.order.id}"

class SupplierReview(models.Model):
    """Customer reviews for suppliers"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='supplier_reviews')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'supplier', 'order')
    
    def __str__(self):
        return f"{self.supplier.name} - {self.rating}/5 - {self.user.username}"
