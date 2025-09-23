# admin_api/views.py

from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny # Permission to check if user is staff and active
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate # For grouping by date
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.utils import timezone # Import timezone
from datetime import timedelta # For date calculations, if needed
from django.db.models import Q # For complex lookups or filtering
# Note: ObtainAuthToken and Token are NOT needed for Simple JWT admin l

# --- Import YOUR specific models from the accounts app and other relevant apps ---
from accounts.models import (
    CustomUser,
     # Your custom user model
    UserSubscription, # Your user subscription model
    # Assuming you have a Payment model in accounts or another app
    # from accounts.models import Payment # Uncomment and adjust if Payment is in accounts
    # If Payment is in a different app, import it like:
    # from payments.models import Payment # Example if you have a payments app
)
# Assuming your estimate/project models are in these paths
from estimates.models import QuickEstimate # Adjust import path if needed
from manual_estimate.models import Estimate as ManualEstimate # Adjust import path and alias if needed
from projects.models import Project # Adjust import path if needed
from suppliers.models import Supplier, SupplierProduct, Order as SupplierOrder

# --- Import your serializers ---
# Assuming these serializers are defined in accounts.serializers
from .serializers import (
    UserSerializer,
    CreateUserSerializer,
    UpdateUserSerializer,
    PermissionSerializer,
    GroupSerializer
)

# Import SMS functionality
from accounts.utils import send_sms_africastalking
from accounts.models import PasswordResetCode
import random
import string

# Get the active user model (which is your CustomUser)
User = get_user_model()


# Note: The AdminLoginView using ObtainAuthToken is removed as we are using Simple JWT


class AdminStatsView(generics.GenericAPIView):
    """
    API endpoint to provide aggregate statistics for the admin dashboard.
    Retrieves data from CustomUser, UserSubscription, Payment, and estimate/project models.
    Requires the user to be an active staff member (IsAdminUser permission).
    """
    permission_classes = [IsAdminUser] # Ensures only staff users can access this view

    def get(self, request, *args, **kwargs):
        # --- 1. Get Total Number of Users ---
        # Query: Count all records in the CustomUser table.
        total_users = CustomUser.objects.count()

        # --- 2. Get Total Number of Paying Users ---
        # Query: Count CustomUser instances linked to active UserSubscription records.
        # Uses the 'subscription' related_name defined on UserSubscription.user ForeignKey.
        # Filter for subscriptions that are active AND whose end_date is in the future
        paying_users_count = CustomUser.objects.filter(
            subscription__is_active=True,
            subscription__end_date__gt=timezone.now()
            # You might also check Payment status associated with the subscription if your flow requires it
            # subscription__payment_status='Paid' # Example if UserSubscription has payment_status
        ).count()
        # Alternative (counting active subscriptions directly):
        # paying_users_count = UserSubscription.objects.filter(is_active=True, end_date__gt=timezone.now()).count()


        # --- 3. Get Total Revenue ---
        # Query: Sum the 'amount' from the Payment table for successful payments.
        # Assumes you have a Payment model with 'amount' and 'status' fields.
        # If you don't have a Payment model or it's structured differently, adjust this.
        # try:
        #     # Import Payment model if it's not already imported above
        #     # from accounts.models import Payment # Example if in accounts app
        #     # from payments.models import Payment # Example if in payments app

        #     # Check if Payment model is available before querying
        #     # if 'Payment' in globals() or 'Payment' in locals(): # Basic check if Payment model was imported
        #     #      total_revenue = Payment.objects.filter(
        #     #          status='Paid' # Filter for successful payments based on your model choices
        #     #          # You might add date filtering here too, e.g., payment_date__year=2024
        #     #      ).aggregate(total=Sum('amount'))['total'] # Sum the 'amount' field
        #     #      total_revenue = total_revenue if total_revenue is not None else 0.00 # Ensure we get 0.00 if no payments found
        #     # else:
        #     #     print("Warning: Payment model not found or imported. Total revenue calculation skipped.")
        #     #     total_revenue = 0.00 # Default to 0 if Payment model isn't available

        # except Exception as e:
        #      print(f"Error calculating total revenue: {e}")
        #      total_revenue = 0.00 # Default to 0 in case of any error


        # --- 4. Get Estimates Per Day ---
        # Query: Count estimates from QuickEstimate, ManualEstimate, and Project
        # models, grouped by creation date.
        today = timezone.now().date()
        start_date = today - timedelta(days=29) # Example: Last 30 days including today

        # Query each model for estimates created within the date range and annotate with date
        # FIX: Renamed annotation from 'date' to 'created_date' to avoid conflict
        quick_estimates_daily_qs = QuickEstimate.objects.filter(
             created_at__date__gte=start_date # Assuming 'created_at' field
        ).annotate(created_date=TruncDate('created_at')).values('created_date').annotate(count=Count('id')) # Use created_date in values()

        manual_estimates_daily_qs = ManualEstimate.objects.filter(
             created_at__date__gte=start_date # Assuming 'created_at' field
        ).annotate(created_date=TruncDate('created_at')).values('created_date').annotate(count=Count('id')) # Use created_date in values()

        project_estimates_daily_qs = Project.objects.filter(
             created_at__date__gte=start_date # Assuming 'created_at' field
        ).annotate(created_date=TruncDate('created_at')).values('created_date').annotate(count=Count('id')) # Use created_date in values()

        # Combine results from all querysets into a single dictionary { 'YYYY-MM-DD': total_count }
        estimates_per_day_dict = {}
        for qs in [quick_estimates_daily_qs, manual_estimates_daily_qs, project_estimates_daily_qs]:
            for entry in qs:
                # Ensure date is a datetime object before formatting
                # Use the new annotation name 'created_date'
                date_obj = entry['created_date'] # FIX: Changed from entry['date'] to entry['created_date']
                date_str = date_obj.strftime('%Y-%m-%d')
                estimates_per_day_dict[date_str] = estimates_per_day_dict.get(date_str, 0) + entry['count']

        # Convert dictionary to a sorted list of objects [{ date: 'YYYY-MM-DD', count: N }] for JSON
        # Use 'date' as the key in the final JSON output for frontend compatibility
        estimates_per_day_list = [{'date': date, 'count': count} for date, count in estimates_per_day_dict.items()]
        estimates_per_day_list = sorted(estimates_per_day_list, key=lambda x: x['date']) # Sort by date


        # --- 5. Get Total Estimates Count (Overall, Manual, Project, 3D Room View) ---
        # Query: Count records in each specific estimate/project table.
        total_quick_estimates = QuickEstimate.objects.count()
        total_manual_estimates = ManualEstimate.objects.count()
        total_project_estimates = Project.objects.count()
        total_estimates_count = total_quick_estimates + total_manual_estimates + total_project_estimates

        # Total 3D Estimates Count
        # Adjust this query based on how you specifically identify 3D projects in your Project model
        # Example: Assuming a boolean field 'includes_3d_view' on your Project model
        total_3d_estimates_count = Project.objects.filter(includes_3d_view=True).count() if hasattr(Project, 'includes_3d_view') else 0
        # Example 2: Assuming a Project has related rooms (via projects_room table) and rooms have a 'has_3d_data' field
        # total_3d_estimates_count = Project.objects.filter(rooms__has_3d_data=True).distinct().count()


        # --- 6. Get Supplier Statistics ---
        total_suppliers = Supplier.objects.count()
        verified_suppliers = Supplier.objects.filter(is_verified=True).count()
        active_suppliers = Supplier.objects.filter(is_active=True).count()
        total_products = SupplierProduct.objects.count()
        active_products = SupplierProduct.objects.filter(in_stock=True).count()
        total_supplier_orders = SupplierOrder.objects.count()
        
        # Revenue from supplier orders
        supplier_revenue = SupplierOrder.objects.filter(status='delivered').aggregate(
            total=Sum('total')
        )['total'] or 0

        # --- 7. Get User Registration Trends ---
        user_registrations_daily = CustomUser.objects.filter(
            date_joined__date__gte=start_date
        ).annotate(created_date=TruncDate('date_joined')).values('created_date').annotate(count=Count('id'))
        
        user_registrations_dict = {}
        for entry in user_registrations_daily:
            date_str = entry['created_date'].strftime('%Y-%m-%d')
            user_registrations_dict[date_str] = entry['count']
        
        user_registrations_list = [{'date': date, 'count': count} for date, count in user_registrations_dict.items()]
        user_registrations_list = sorted(user_registrations_list, key=lambda x: x['date'])

        # --- 8. Get Revenue Trends ---
        subscription_revenue = UserSubscription.objects.filter(
            is_active=True,
            payment_status='Paid'
        ).aggregate(total=Sum('plan__price'))['total'] or 0

        # --- 9. Get Active Users (logged in within last 30 days) ---
        thirty_days_ago = timezone.now() - timedelta(days=30)
        active_users = CustomUser.objects.filter(last_login__gte=thirty_days_ago).count()

        # --- 10. Get Top Performing Suppliers ---
        top_suppliers = Supplier.objects.filter(is_verified=True).order_by('-rating', '-total_orders')[:5]
        top_suppliers_data = [
            {
                'id': supplier.id,
                'name': supplier.name,
                'city': supplier.city,
                'rating': float(supplier.rating),
                'total_orders': supplier.total_orders,
                'products_count': supplier.products.count()
            }
            for supplier in top_suppliers
        ]

        # --- Prepare Enhanced Response Data ---
        stats_data = {
            # User Statistics
            'total_users': total_users,
            'paying_users_count': paying_users_count,
            'active_users': active_users,
            'user_registrations_daily': user_registrations_list,
            
            # Estimate Statistics
            'total_estimates_count': total_estimates_count,
            'total_manual_estimates_count': total_manual_estimates,
            'total_project_estimates_count': total_project_estimates,
            'total_3d_estimates_count': total_3d_estimates_count,
            'estimates_per_day': estimates_per_day_list,
            
            # Supplier Statistics
            'total_suppliers': total_suppliers,
            'verified_suppliers': verified_suppliers,
            'active_suppliers': active_suppliers,
            'total_products': total_products,
            'active_products': active_products,
            'total_supplier_orders': total_supplier_orders,
            'top_suppliers': top_suppliers_data,
            
            # Revenue Statistics
            'subscription_revenue': float(subscription_revenue),
            'supplier_revenue': float(supplier_revenue),
            'total_revenue': float(subscription_revenue + supplier_revenue),
            
            # Quick Insights
            'conversion_rate': round((paying_users_count / total_users * 100), 2) if total_users > 0 else 0,
            'supplier_verification_rate': round((verified_suppliers / total_suppliers * 100), 2) if total_suppliers > 0 else 0,
            'average_estimates_per_user': round((total_estimates_count / total_users), 2) if total_users > 0 else 0,
        }

        return Response(stats_data)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users (List, Create, Retrieve, Update, Delete).
    Works with your CustomUser model.
    Requires the user to be an active staff member (IsAdminUser permission).
    """
    # --- Get all CustomUser objects ---
    queryset = CustomUser.objects.all().order_by('-date_joined') # Order by newest users first
    permission_classes = [IsAdminUser] # Ensures only staff users can access this view

    # Determine which serializer to use based on the action (create vs list/retrieve/update)
    def get_serializer_class(self):
        if self.action == 'create':
            # Use the serializer designed for creating users with password hashing
            return CreateUserSerializer
        elif self.action in ['update', 'partial_update']:
            # Use the serializer designed for updating user fields
            return UpdateUserSerializer
        # Default serializer for 'list', 'retrieve', and any other actions
        # This includes the 'is_paying' field calculated in the serializer
        return UserSerializer

    # --- Actions implemented by ModelViewSet ---
    # list: Handles GET /api/admin/users/ -> Uses UserSerializer, queries queryset, supports pagination
    # create: Handles POST /api/admin/users/ -> Uses CreateUserSerializer, saves a new CustomUser
    # retrieve: Handles GET /api/admin/users/{pk}/ -> Uses UserSerializer, gets one CustomUser by ID
    # update: Handles PUT /api/admin/users/{pk}/ -> Uses UpdateUserSerializer, updates one CustomUser by ID (full update)
    # partial_update: Handles PATCH /api/admin/users/{pk}/ -> Uses UpdateUserSerializer, updates one CustomUser by ID (partial update)
    # destroy: Handles DELETE /api/admin/users/{pk}/ -> Deletes one CustomUser by ID


    # --- Optional: Add filtering capabilities (requires django-filter) ---
    # Example:
    # from django_filters.rest_framework import DjangoFilterBackend
    # from rest_framework import filters
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    # filterset_fields = ['is_active', 'is_staff', 'is_superuser'] # Allow filtering by these boolean fields
    # search_fields = ['username', 'email', 'phone_number'] # Allow searching by these text fields

    # --- Optional: Add pagination ---
    # Configure pagination in settings.py or add pagination_class here
    # Example:
    # from rest_framework.pagination import PageNumberPagination
    # class StandardResultsSetPagination(PageNumberPagination):
    #     page_size = 10
    #     page_size_query_param = 'limit'
    #     max_page_size = 100
    # pagination_class = StandardResultsSetPagination

# Password Reset with SMS functionality
@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset_sms(request):
    """Send password reset code via SMS using Africa's Talking"""
    phone_number = request.data.get('phone_number')
    
    if not phone_number:
        return Response(
            {"error": "Phone number is required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Normalize phone number format
    def normalize_phone(phone):
        digits = ''.join(filter(str.isdigit, phone))
        if digits.startswith('0') and len(digits) == 10:
            return '+233' + digits[1:]
        elif digits.startswith('233') and len(digits) == 12:
            return '+' + digits
        elif len(digits) == 9:
            return '+233' + digits
        return phone
    
    normalized_phone = normalize_phone(phone_number)
    
    try:
        # Find user by phone number
        user = CustomUser.objects.filter(phone_number=normalized_phone).first()
        
        if not user:
            return Response(
                {"error": "No user found with this phone number"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generate reset code
        reset_code = ''.join(random.choices(string.digits, k=6))
        
        # Delete any existing reset codes for this user
        PasswordResetCode.objects.filter(user=user).delete()
        
        # Create new reset code
        PasswordResetCode.objects.create(
            user=user,
            code=reset_code,
            expires_at=timezone.now() + timedelta(minutes=15)  # 15 minutes expiry
        )
        
        # Send SMS
        message = f"Your TILNET password reset code is: {reset_code}. This code expires in 15 minutes. If you didn't request this, please ignore."
        
        sms_response = send_sms_africastalking(to=normalized_phone, message=message)
        
        if sms_response and sms_response.get('SMSMessageData', {}).get('Recipients'):
            recipients = sms_response['SMSMessageData']['Recipients']
            if recipients and recipients[0].get('status') == 'Success':
                return Response(
                    {"message": "Password reset code sent successfully"}, 
                    status=status.HTTP_200_OK
                )
        
        return Response(
            {"error": "Failed to send SMS. Please try again."}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
    except Exception as e:
        print(f"Error in password reset SMS: {e}")
        return Response(
            {"error": "An error occurred while processing your request"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_password_reset_code(request):
    """Verify password reset code and allow password change"""
    phone_number = request.data.get('phone_number')
    code = request.data.get('code')
    new_password = request.data.get('new_password')
    
    if not all([phone_number, code, new_password]):
        return Response(
            {"error": "Phone number, code, and new password are required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Normalize phone number
    def normalize_phone(phone):
        digits = ''.join(filter(str.isdigit, phone))
        if digits.startswith('0') and len(digits) == 10:
            return '+233' + digits[1:]
        elif digits.startswith('233') and len(digits) == 12:
            return '+' + digits
        elif len(digits) == 9:
            return '+233' + digits
        return phone
    
    normalized_phone = normalize_phone(phone_number)
    
    try:
        # Find user and reset code
        user = CustomUser.objects.filter(phone_number=normalized_phone).first()
        
        if not user:
            return Response(
                {"error": "No user found with this phone number"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        reset_code_obj = PasswordResetCode.objects.filter(
            user=user,
            code=code,
            expires_at__gt=timezone.now(),
            is_used=False
        ).first()
        
        if not reset_code_obj:
            return Response(
                {"error": "Invalid or expired reset code"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Mark reset code as used
        reset_code_obj.is_used = True
        reset_code_obj.save()
        
        # Send confirmation SMS
        confirmation_message = f"Your TILNET password has been successfully reset. If this wasn't you, please contact support immediately."
        send_sms_africastalking(to=normalized_phone, message=confirmation_message)
        
        return Response(
            {"message": "Password reset successfully"}, 
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        print(f"Error in password reset verification: {e}")
        return Response(
            {"error": "An error occurred while resetting your password"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


    # --- Optional: Custom Actions for Managing User Permissions/Groups ---
    # You could add actions here or use separate views (as discussed before)
    # Example action to set a user's groups (requires the UserGroupsView logic or similar)
    # from rest_framework.decorators import action
    # @action(detail=True, methods=['get', 'put'])
    # def groups(self, request, pk=None):
    #     """Get or Set a user's group memberships."""
    #     user = self.get_object() # Gets the CustomUser instance
    #     if request.method == 'GET':
    #         # Return the IDs of groups the user belongs to
    #         group_ids = user.groups.values_list('id', flat=True)
    #         return Response(list(group_ids))
    #     elif request.method == 'PUT':
    #         # Expect list of group IDs in the request body
    #         group_ids = request.data.get('group_ids', [])
    #         # Validate and update user's groups relation
    #         groups_to_set = Group.objects.filter(id__in=group_ids)
    #         if len(groups_to_set) != len(group_ids):
    #             return Response({'detail': 'Invalid group ID(s) provided.'}, status=400)
    #         user.groups.set(groups_to_set) # Update the many-to-many relation
    #         return Response({'status': 'Groups updated successfully'})


class PermissionListView(generics.ListAPIView):
    """
    API endpoint to list all available Django Permissions (from auth_permission).
    Useful for a user permission management interface in the admin frontend.
    Requires the user to be an active staff member (IsAdminUser permission).
    """
    # --- Get all Django Permission objects ---
    queryset = Permission.objects.all().order_by('name') # Order alphabetically by name
    serializer_class = PermissionSerializer
    permission_classes = [IsAdminUser]


class GroupListView(generics.ListAPIView):
    """
    API endpoint to list all available Django Groups (from auth_group).
    Useful for a user group management interface in the admin frontend.
    Requires the user to be an active staff member (IsAdminUser permission).
    """
    # --- Get all Django Group objects ---
    queryset = Group.objects.all().order_by('name') # Order alphabetically by name
    serializer_class = GroupSerializer
    permission_classes = [IsAdminUser]

# --- If you prefer separate views for managing user permissions/groups ---
# You would define views like UserGroupsView or UserPermissionsView here
# and add their URLs in admin_api/urls.py
