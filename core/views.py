from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.core.paginator import Paginator
from .serializers import (
    UserSerializer, LoginSerializer, ProfileDetailSerializer,
    ProfileUpdateSerializer, DepartmentSerializer, DepartmentCreateSerializer,
    RoleSerializer, CreateUserSerializer, ManageUserSerializer, BranchSerializer , ProfileChangePasswordSerializer ,ResetPasswordSerializer, ForgotPasswordSerializer
)
from .models import Department, Role, User, Branch
from .permissions import RoleBasedPermission  # Import the custom permission
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
import logging

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'name': user.first_name,
                    'email': user.email,
                    'profilePic': user.profile.profilePic,
                    'jobRole': user.profile.role.name if user.profile.role else None,
                    'mobile': user.profile.phone,
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from .models import Profile

# views.py (LoginView section)
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            if user:
                token, created = Token.objects.get_or_create(user=user)
                # Set session expiry based on remember_me
                if not serializer.validated_data.get('remember_me', True):
                    request.session.set_expiry(0)  # Expires on browser close
                else:
                    request.session.set_expiry(1209600)  # 2 weeks (1,209,600 seconds)
                return Response({
                    'token': token.key,
                    'user': {
                        'id': user.id,
                        'name': user.first_name,
                        'email': user.email,
                        'profilePic': user.profile.profilePic.url if user.profile.profilePic else None,  # Use .url
                        'jobRole': user.profile.role.role if user.profile.role else None,
                        'mobile': user.profile.contact_number,
                    }
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                reset_token = get_random_string(length=32)
                profile = user.profile
                profile.reset_token = reset_token
                profile.reset_token_expiry = timezone.now() + timezone.timedelta(minutes=30)  # 30-minute expiry
                profile.save()

                reset_link = f"http://yourdomain.com/reset-password/{reset_token}/"
                subject = 'Password Reset Request'
                message = f'Click the link to reset your password: {reset_link}'
                from_email = settings.EMAIL_HOST_USER
                send_mail(subject, message, from_email, [email], fail_silently=False)

                return Response({'redirect': '/check-email', 'email': email}, status=status.HTTP_200_OK)
            except (User.DoesNotExist, Profile.DoesNotExist):
                return Response({'error': 'Email not registered'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, token):
        try:
            profile = Profile.objects.get(reset_token=token, reset_token_expiry__gt=timezone.now())
            serializer = ResetPasswordSerializer(data=request.data)
            if serializer.is_valid():
                user = profile.user
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                profile.reset_token = None
                profile.reset_token_expiry = None
                profile.save()
                return Response({'message': 'Password reset successful. Please log in.', 'redirect': '/login'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)



from rest_framework.pagination import PageNumberPagination
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    BranchSerializer, DepartmentSerializer, DepartmentDropdownSerializer,
    DepartmentCreateSerializer, RoleSerializer, RoleUpdateSerializer,
    ProfileDetailSerializer, ProfileUpdateSerializer
)
from .models import Branch, Department, Role, Profile

class RoleBasedPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Placeholder: Implement your role-based permission logic here
        return request.user.is_authenticated

class BranchListView(APIView):
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]

    def get(self, request):
        branches = Branch.objects.all()
        serializer = BranchSerializer(branches, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = BranchSerializer(data=request.data)
        if serializer.is_valid():
            branch = serializer.save()
            return Response(BranchSerializer(branch).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BranchDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]

    def get(self, request, pk):
        try:
            branch = Branch.objects.get(pk=pk)
            serializer = BranchSerializer(branch)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Branch.DoesNotExist:
            return Response({'error': 'Branch not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            branch = Branch.objects.get(pk=pk)
            serializer = BranchSerializer(branch, data=request.data, partial=True)
            if serializer.is_valid():
                branch = serializer.save()
                return Response(BranchSerializer(branch).data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Branch.DoesNotExist:
            return Response({'error': 'Branch not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            branch = Branch.objects.get(pk=pk)
            branch.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Branch.DoesNotExist:
            return Response({'error': 'Branch not found'}, status=status.HTTP_404_NOT_FOUND)

class DepartmentListView(APIView):
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 5))
        branch_id = request.query_params.get('branch')
        dropdown = request.query_params.get('dropdown', 'false').lower() == 'true'
        include_roles = request.query_params.get('include_roles', 'false').lower() == 'true'

        departments = Department.objects.all()
        if branch_id:
            try:
                departments = departments.filter(branch_id=branch_id)
            except ValueError:
                return Response({'error': 'Invalid branch ID'}, status=status.HTTP_400_BAD_REQUEST)

        paginator = PageNumberPagination()
        paginator.page_size = per_page
        page_obj = paginator.paginate_queryset(departments, request)

        if dropdown:
            serializer = DepartmentDropdownSerializer(page_obj, many=True)
        else:
            serializer = DepartmentSerializer(page_obj, many=True, context={'include_roles': include_roles})

        return Response({
            'departments': serializer.data,
            'total_pages': paginator.page.paginator.num_pages,
            'current_page': page,
            'total_entries': departments.count(),
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = DepartmentCreateSerializer(data=request.data)
        if serializer.is_valid():
            department = serializer.save()
            return Response(DepartmentSerializer(department).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DepartmentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]

    def get(self, request, pk):
        try:
            department = Department.objects.get(pk=pk)
            serializer = DepartmentSerializer(department)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Department.DoesNotExist:
            return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            department = Department.objects.get(pk=pk)
            serializer = DepartmentCreateSerializer(department, data=request.data, partial=True)
            if serializer.is_valid():
                department = serializer.save()
                return Response(DepartmentSerializer(department).data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Department.DoesNotExist:
            return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            department = Department.objects.get(pk=pk)
            department.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Department.DoesNotExist:
            return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)

class RoleView(APIView):
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 10))
        department_id = request.query_params.get('department')

        roles = Role.objects.all().order_by('id')
        if department_id:
            try:
                roles = roles.filter(department_id=department_id)
            except ValueError:
                return Response({'error': 'Invalid department ID'}, status=status.HTTP_400_BAD_REQUEST)

        paginator = PageNumberPagination()
        paginator.page_size = per_page
        page_obj = paginator.paginate_queryset(roles, request)
        serializer = RoleSerializer(page_obj, many=True)

        return Response({
            'roles': serializer.data,
            'total_pages': paginator.page.paginator.num_pages,
            'current_page': page,
            'total_entries': roles.count(),
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = RoleUpdateSerializer(data=request.data)
        if serializer.is_valid():
            role = serializer.save()
            return Response(RoleSerializer(role).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoleDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]

    def get(self, request, pk=None):
        if pk:
            try:
                role = Role.objects.get(pk=pk)
                serializer = RoleSerializer(role)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Role.DoesNotExist:
                return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            page = int(request.query_params.get('page', 1))
            per_page = int(request.query_params.get('per_page', 10))
            department_id = request.query_params.get('department')

            roles = Role.objects.all().order_by('id')
            if department_id:
                try:
                    roles = roles.filter(department_id=department_id)
                except ValueError:
                    return Response({'error': 'Invalid department ID'}, status=status.HTTP_400_BAD_REQUEST)

            paginator = PageNumberPagination()
            paginator.page_size = per_page
            page_obj = paginator.paginate_queryset(roles, request)
            serializer = RoleSerializer(page_obj, many=True)

            return Response({
                'roles': serializer.data,
                'total_pages': paginator.page.paginator.num_pages,
                'current_page': page,
                'total_entries': roles.count(),
            }, status=status.HTTP_200_OK)

    def put(self, request, pk):
        try:
            role = Role.objects.get(pk=pk)
            serializer = RoleUpdateSerializer(role, data=request.data, partial=True)
            if serializer.is_valid():
                role = serializer.save()
                return Response(RoleSerializer(role).data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Role.DoesNotExist:
            return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            role = Role.objects.get(pk=pk)
            role.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Role.DoesNotExist:
            return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.profile
            serializer = ProfileDetailSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:
            profile = request.user.profile
            data = request.data.copy() if hasattr(request.data, 'copy') else request.data
            password_data = {
                'password': data.pop('password', None),
                'confirm_password': data.pop('confirm_password', None)
            }

            serializer = ProfileUpdateSerializer(profile, data=data, partial=True)
            if serializer.is_valid():
                profile = serializer.save()

                if password_data['password'] and password_data['confirm_password']:
                    password_serializer = ProfileChangePasswordSerializer(data=password_data)
                    if password_serializer.is_valid():
                        password_serializer.update(request.user, password_serializer.validated_data)
                    else:
                        return Response(password_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                return Response(ProfileDetailSerializer(profile).data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

class ManageUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 10))
        users = User.objects.all().order_by('id')
        paginator = Paginator(users, per_page)
        page_obj = paginator.get_page(page)
        serializer = ManageUserSerializer(page_obj, many=True)
        return Response({
            'users': serializer.data,
            'total_pages': paginator.num_pages,
            'current_page': page,
            'total_entries': users.count(),
        }, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can add users'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            password = get_random_string(length=8, allowed_chars='abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*')
            profile_data = request.data.get('profile', {})

            # Use request data directly for user fields
            user_data = {
                'first_name': request.data.get('first_name'),
                'last_name': request.data.get('last_name', ''),
                'email': request.data.get('email'),
                'profile': profile_data
            }

            user_serializer = CreateUserSerializer(data=user_data)
            if user_serializer.is_valid():
                user = user_serializer.save(password=password)
            else:
                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Send email with password
            subject = 'Your Account Credentials'
            message = f"""
            Hello {user.first_name},

            Your account has been created with the following details:
            - Email: {user.email}
            - Temporary Password: {password}

            Please change your password after logging in by visiting your profile page. Follow these steps:
            1. Log in with the above credentials.
            2. Go to your profile settings.
            3. Update your password under the security section.

            Regards,
            Your Admin Team
            """
            from_email = settings.DEFAULT_FROM_EMAIL
            try:
                send_mail(
                    subject,
                    message,
                    from_email,
                    [user.email],
                    fail_silently=False,
                )
                logger.info(f"Email sent to {user.email}")
            except Exception as e:
                logger.error(f"Failed to send email to {user.email}: {str(e)}")
                return Response({'error': 'User created but email failed to send'}, status=status.HTTP_201_CREATED)

            return Response(ManageUserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ManageUserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]

    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            serializer = ManageUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            serializer = CreateUserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                user = serializer.save()
                return Response(ManageUserSerializer(user).data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Product, Category, TaxCode, UOM, Warehouse, Size, Color, Supplier
from .serializers import ProductSerializer, CategorySerializer, TaxCodeSerializer, UOMSerializer, WarehouseSerializer, SizeSerializer, ColorSerializer, SupplierSerializer
from django.core.paginator import Paginator
import pandas as pd
from django.core.files.storage import default_storage
from .permissions import RoleBasedPermission  # Assuming this exists

class ProductListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 10))
        products = Product.objects.all()
        paginator = Paginator(products, per_page)
        page_obj = paginator.get_page(page)
        serializer = ProductSerializer(page_obj, many=True)
        return Response({
            'products': serializer.data,
            'total_pages': paginator.num_pages,
            'current_page': page,
            'total_entries': products.count(),
        }, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can add products'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can edit products'}, status=status.HTTP_403_FORBIDDEN)
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can delete products'}, status=status.HTTP_403_FORBIDDEN)
        try:
            product = Product.objects.get(pk=pk)
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

class ProductImportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can import products'}, status=status.HTTP_403_FORBIDDEN)
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        required_fields = ['product_id', 'name', 'product_type', 'category', 'status', 'stock_level', 'unit_price']
        missing_fields = [field for field in required_fields if field not in df.columns]
        if missing_fields:
            return Response({'error': f'Missing required fields: {missing_fields}'}, status=status.HTTP_400_BAD_REQUEST)

        valid_rows = []
        invalid_rows = []
        skipped_rows = []

        seen_product_ids = set()
        seen_product_names = set()

        for index, row in df.iterrows():
            if not all(row[field] for field in required_fields):
                invalid_rows.append(index)
                continue

            product_id = str(row['product_id'])
            product_name = str(row['name'])
            if product_id in seen_product_ids or product_name in seen_product_names:
                skipped_rows.append(index)
                continue

            seen_product_ids.add(product_id)
            seen_product_names.add(product_name)
            valid_rows.append(row.to_dict())

        for row in valid_rows:
            serializer = ProductSerializer(data=row)
            if serializer.is_valid():
                serializer.save()
            else:
                invalid_rows.append(row)

        return Response({
            'valid_rows': len(valid_rows),
            'invalid_rows': len(invalid_rows),
            'skipped_rows': len(skipped_rows)
        }, status=status.HTTP_201_CREATED)

class CategoryListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 10))
        categories = Category.objects.all()
        paginator = Paginator(categories, per_page)
        page_obj = paginator.get_page(page)
        serializer = CategorySerializer(page_obj, many=True)
        return Response({
            'categories': serializer.data,
            'total_pages': paginator.num_pages,
            'current_page': page,
            'total_entries': categories.count(),
        }, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can add categories'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can edit categories'}, status=status.HTTP_403_FORBIDDEN)
        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can delete categories'}, status=status.HTTP_403_FORBIDDEN)
        try:
            category = Category.objects.get(pk=pk)
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

class TaxCodeListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 10))
        tax_codes = TaxCode.objects.all()
        paginator = Paginator(tax_codes, per_page)
        page_obj = paginator.get_page(page)
        serializer = TaxCodeSerializer(page_obj, many=True)
        return Response({
            'tax_codes': serializer.data,
            'total_pages': paginator.num_pages,
            'current_page': page,
            'total_entries': tax_codes.count(),
        }, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can add tax codes'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TaxCodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaxCodeDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            tax_code = TaxCode.objects.get(pk=pk)
            serializer = TaxCodeSerializer(tax_code)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except TaxCode.DoesNotExist:
            return Response({'error': 'Tax code not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can edit tax codes'}, status=status.HTTP_403_FORBIDDEN)
        try:
            tax_code = TaxCode.objects.get(pk=pk)
            serializer = TaxCodeSerializer(tax_code, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except TaxCode.DoesNotExist:
            return Response({'error': 'Tax code not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can delete tax codes'}, status=status.HTTP_403_FORBIDDEN)
        try:
            tax_code = TaxCode.objects.get(pk=pk)
            tax_code.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TaxCode.DoesNotExist:
            return Response({'error': 'Tax code not found'}, status=status.HTTP_404_NOT_FOUND)

class UOMListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 10))
        uoms = UOM.objects.all()
        paginator = Paginator(uoms, per_page)
        page_obj = paginator.get_page(page)
        serializer = UOMSerializer(page_obj, many=True)
        return Response({
            'uoms': serializer.data,
            'total_pages': paginator.num_pages,
            'current_page': page,
            'total_entries': uoms.count(),
        }, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can add UOMs'}, status=status.HTTP_403_FORBIDDEN)
        serializer = UOMSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UOMDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            uom = UOM.objects.get(pk=pk)
            serializer = UOMSerializer(uom)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UOM.DoesNotExist:
            return Response({'error': 'UOM not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can edit UOMs'}, status=status.HTTP_403_FORBIDDEN)
        try:
            uom = UOM.objects.get(pk=pk)
            serializer = UOMSerializer(uom, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UOM.DoesNotExist:
            return Response({'error': 'UOM not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can delete UOMs'}, status=status.HTTP_403_FORBIDDEN)
        try:
            uom = UOM.objects.get(pk=pk)
            uom.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UOM.DoesNotExist:
            return Response({'error': 'UOM not found'}, status=status.HTTP_404_NOT_FOUND)

class WarehouseListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 10))
        warehouses = Warehouse.objects.all()
        paginator = Paginator(warehouses, per_page)
        page_obj = paginator.get_page(page)
        serializer = WarehouseSerializer(page_obj, many=True)
        return Response({
            'warehouses': serializer.data,
            'total_pages': paginator.num_pages,
            'current_page': page,
            'total_entries': warehouses.count(),
        }, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can add warehouses'}, status=status.HTTP_403_FORBIDDEN)
        serializer = WarehouseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WarehouseDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            warehouse = Warehouse.objects.get(pk=pk)
            serializer = WarehouseSerializer(warehouse)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Warehouse.DoesNotExist:
            return Response({'error': 'Warehouse not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can edit warehouses'}, status=status.HTTP_403_FORBIDDEN)
        try:
            warehouse = Warehouse.objects.get(pk=pk)
            serializer = WarehouseSerializer(warehouse, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Warehouse.DoesNotExist:
            return Response({'error': 'Warehouse not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can delete warehouses'}, status=status.HTTP_403_FORBIDDEN)
        try:
            warehouse = Warehouse.objects.get(pk=pk)
            warehouse.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Warehouse.DoesNotExist:
            return Response({'error': 'Warehouse not found'}, status=status.HTTP_404_NOT_FOUND)

class SizeListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 10))
        sizes = Size.objects.all()
        paginator = Paginator(sizes, per_page)
        page_obj = paginator.get_page(page)
        serializer = SizeSerializer(page_obj, many=True)
        return Response({
            'sizes': serializer.data,
            'total_pages': paginator.num_pages,
            'current_page': page,
            'total_entries': sizes.count(),
        }, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can add sizes'}, status=status.HTTP_403_FORBIDDEN)
        serializer = SizeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SizeDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            size = Size.objects.get(pk=pk)
            serializer = SizeSerializer(size)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Size.DoesNotExist:
            return Response({'error': 'Size not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can edit sizes'}, status=status.HTTP_403_FORBIDDEN)
        try:
            size = Size.objects.get(pk=pk)
            serializer = SizeSerializer(size, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Size.DoesNotExist:
            return Response({'error': 'Size not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can delete sizes'}, status=status.HTTP_403_FORBIDDEN)
        try:
            size = Size.objects.get(pk=pk)
            size.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Size.DoesNotExist:
            return Response({'error': 'Size not found'}, status=status.HTTP_404_NOT_FOUND)

class ColorListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 10))
        colors = Color.objects.all()
        paginator = Paginator(colors, per_page)
        page_obj = paginator.get_page(page)
        serializer = ColorSerializer(page_obj, many=True)
        return Response({
            'colors': serializer.data,
            'total_pages': paginator.num_pages,
            'current_page': page,
            'total_entries': colors.count(),
        }, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can add colors'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ColorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ColorDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            color = Color.objects.get(pk=pk)
            serializer = ColorSerializer(color)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Color.DoesNotExist:
            return Response({'error': 'Color not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can edit colors'}, status=status.HTTP_403_FORBIDDEN)
        try:
            color = Color.objects.get(pk=pk)
            serializer = ColorSerializer(color, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Color.DoesNotExist:
            return Response({'error': 'Color not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can delete colors'}, status=status.HTTP_403_FORBIDDEN)
        try:
            color = Color.objects.get(pk=pk)
            color.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Color.DoesNotExist:
            return Response({'error': 'Color not found'}, status=status.HTTP_404_NOT_FOUND)

class SupplierListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 10))
        suppliers = Supplier.objects.all()
        paginator = Paginator(suppliers, per_page)
        page_obj = paginator.get_page(page)
        serializer = SupplierSerializer(page_obj, many=True)
        return Response({
            'suppliers': serializer.data,
            'total_pages': paginator.num_pages,
            'current_page': page,
            'total_entries': suppliers.count(),
        }, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can add suppliers'}, status=status.HTTP_403_FORBIDDEN)
        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SupplierDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            supplier = Supplier.objects.get(pk=pk)
            serializer = SupplierSerializer(supplier)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Supplier.DoesNotExist:
            return Response({'error': 'Supplier not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can edit suppliers'}, status=status.HTTP_403_FORBIDDEN)
        try:
            supplier = Supplier.objects.get(pk=pk)
            serializer = SupplierSerializer(supplier, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Supplier.DoesNotExist:
            return Response({'error': 'Supplier not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can delete suppliers'}, status=status.HTTP_403_FORBIDDEN)
        try:
            supplier = Supplier.objects.get(pk=pk)
            supplier.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Supplier.DoesNotExist:
            return Response({'error': 'Supplier not found'}, status=status.HTTP_404_NOT_FOUND)
        

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Candidate, Department, Branch, Role
from .serializers import CandidateSerializer, DepartmentSerializer, BranchSerializer, RoleSerializer
from django.core.paginator import Paginator
from rest_framework.parsers import MultiPartParser, FormParser
import os, uuid
from django.conf import settings
from django.core.files.storage import default_storage

import os
import logging

logger = logging.getLogger(__name__)

# class OnboardingListView(APIView):
#     def post(self, request, format=None):
#         logger.info("Received POST request with data: %s", request.data)
#         logger.info("Received FILES: %s", request.FILES)

#         data = request.data.copy()
#         file_paths = []

#         upload_documents = request.FILES.getlist('upload_documents')
#         logger.info("Files in upload_documents: %s", [f.name for f in upload_documents])

#         try:
#             for file in upload_documents:
#                 # Sanitize and generate unique file name
#                 file_name, file_ext = os.path.splitext(default_storage.get_valid_name(file.name))
#                 unique_name = f"{file_name}_{uuid.uuid4().hex[:8]}{file_ext}"
#                 save_path = os.path.join('media/documents', unique_name)
#                 saved_path = default_storage.save(save_path, file)
#                 logger.info("Saved file: %s", saved_path)
#                 file_paths.append(saved_path)
#         except Exception as e:
#             logger.error("Error processing files: %s", str(e))
#             return Response(
#                 {'error': f'Failed to process uploaded files: {str(e)}'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # Set upload_documents as a comma-separated string
#         data['upload_documents'] = ','.join(file_paths) if file_paths else ''
#         logger.info("Data before serialization: %s", data)

#         serializer = CandidateSerializer(data=data)
#         if serializer.is_valid():
#             candidate = serializer.save()
#             logger.info("Candidate saved successfully with upload_documents: %s", candidate.upload_documents)
#             return Response(
#                 {'message': 'Data submitted successfully', 'data': serializer.data},
#                 status=status.HTTP_201_CREATED
#             )
#         logger.error("Serializer errors: %s", serializer.errors)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Candidate, CandidateDocument
from .serializers import CandidateSerializer
import logging
import os
import uuid
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)

class OnboardingListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        try:
            candidates = Candidate.objects.select_related('department', 'branch', 'designation').all()
            serializer = CandidateSerializer(candidates, many=True)
            logger.info("Fetched %d candidates", candidates.count())
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Error fetching candidates: %s", str(e))
            return Response(
                {"error": "Failed to fetch candidates"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, format=None):
        logger.info("Received POST request with data keys: %s", list(request.data.keys()))
        logger.info("Received FILES: %s", list(request.FILES.keys()))

        upload_documents = request.FILES.getlist('upload_documents')
        data = request.data.dict() if hasattr(request.data, 'dict') else request.data

        # Prepare document data for serializer
        documents_data = []
        for file in upload_documents:
            file_name, file_ext = os.path.splitext(file.name)
            unique_name = f"{file_name}_{uuid.uuid4().hex[:8]}{file_ext}"
            save_path = os.path.join('candidate_documents', unique_name)
            saved_path = default_storage.save(save_path, file)
            documents_data.append({'file': saved_path})

        data['upload_documents'] = documents_data
        serializer = CandidateSerializer(data=data)
        if serializer.is_valid():
            candidate = serializer.save()
            logger.info("Candidate saved successfully with %d documents", len(candidate.upload_documents.all()))
            return Response(
                {'message': 'Data submitted successfully', 'data': CandidateSerializer(candidate).data},
                status=status.HTTP_201_CREATED
            )
        logger.error("Serializer errors: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OnboardingDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            candidate = Candidate.objects.select_related('department', 'branch', 'designation').get(pk=pk)
            serializer = CandidateSerializer(candidate)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can edit candidates'}, status=status.HTTP_403_FORBIDDEN)
        try:
            candidate = Candidate.objects.get(pk=pk)
            upload_documents = request.FILES.getlist('upload_documents')
            data = request.data.dict() if hasattr(request.data, 'dict') else request.data

            # Prepare new document data
            documents_data = []
            for file in upload_documents:
                file_name, file_ext = os.path.splitext(file.name)
                unique_name = f"{file_name}_{uuid.uuid4().hex[:8]}{file_ext}"
                save_path = os.path.join('Candidate_documents', unique_name)
                saved_path = default_storage.save(save_path, file)
                documents_data.append({'file': saved_path})

            data['upload_documents'] = documents_data
            serializer = CandidateSerializer(candidate, data=data, partial=True)
            if serializer.is_valid():
                candidate = serializer.save()
                logger.info("Candidate updated with %d documents", len(candidate.upload_documents.all()))
                return Response(CandidateSerializer(candidate).data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Only super admins can delete candidates'}, status=status.HTTP_403_FORBIDDEN)
        try:
            candidate = Candidate.objects.get(pk=pk)
            candidate.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)
        

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from django.utils import timezone
from .models import Attendance, GovernmentHoliday
from .serializers import AttendanceSerializer, CheckInOutSerializer, GovernmentHolidaySerializer
from django.contrib.auth.models import User

class AttendanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        attendance_data = Attendance.objects.filter(user=user).order_by('date')
        serializer = AttendanceSerializer(attendance_data, many=True)
        return Response(serializer.data)

class CheckInOutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = CheckInOutSerializer(data=request.data)
        if serializer.is_valid():
            date = serializer.validated_data['date']
            is_check_in = serializer.validated_data['is_check_in']
            current_date = timezone.now().date()

            # Prevent past date operations
            if date < current_date:
                return Response({"error": "Cannot check-in/out for past dates"}, status=status.HTTP_400_BAD_REQUEST)
            if date > current_date:
                return Response({"error": "Cannot check-in/out for future dates"}, status=status.HTTP_400_BAD_REQUEST)

            attendance, created = Attendance.objects.get_or_create(
                user=user,
                date=date,
                defaults={'check_in_times': [], 'total_hours': 0.0}
            )

            check_in_times = attendance.check_in_times
            now = timezone.now().isoformat()

            if is_check_in:
                if len(check_in_times) % 2 == 0:  # Even: Allow check-in
                    check_in_times.append(now)
                else:
                    return Response({"error": "Already checked in. Check out first."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if len(check_in_times) % 2 == 1:  # Odd: Allow check-out
                    check_in_times.append(now)
                else:
                    return Response({"error": "Not checked in yet."}, status=status.HTTP_400_BAD_REQUEST)

            # Calculate total hours
            total_hours = 0.0
            times = [timezone.datetime.fromisoformat(t) for t in check_in_times]
            for i in range(0, len(times) - 1, 2):
                if i + 1 < len(times):
                    total_hours += (times[i + 1] - times[i]).total_seconds() / 3600

            attendance.check_in_times = check_in_times
            attendance.total_hours = round(total_hours, 2)
            attendance.save()

            serializer = AttendanceSerializer(attendance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GovernmentHolidayView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        holidays = GovernmentHoliday.objects.all()
        serializer = GovernmentHolidaySerializer(holidays, many=True)
        return Response(serializer.data)
    


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.paginator import Paginator
from .models import Task
from .serializers import TaskSerializer, UserSerializer
from django.contrib.auth.models import User

class TaskListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 10))
        tasks = Task.objects.filter(assigned_to=request.user).order_by('due_date')
        paginator = Paginator(tasks, per_page)
        page_obj = paginator.get_page(page)
        serializer = TaskSerializer(page_obj, many=True)
        return Response({
            'tasks': serializer.data,
            'total_pages': paginator.num_pages,
            'current_page': page,
            'total_entries': tasks.count(),
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(assigned_to=request.user)  # Default to current user for now
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            task = Task.objects.get(pk=pk, assigned_to=request.user)
            serializer = TaskSerializer(task)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            task = Task.objects.get(pk=pk, assigned_to=request.user)
            serializer = TaskSerializer(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            task = Task.objects.get(pk=pk, assigned_to=request.user)
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

class TaskSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(assigned_to=request.user)
        summary = {
            'not_started': tasks.filter(status='Not Started').count(),
            'in_progress': tasks.filter(status='In Progress').count(),
            'completed': tasks.filter(status='Completed').count(),
            'awaiting_feedback': tasks.filter(status='Awaiting Feedback').count(),
        }
        return Response(summary, status=status.HTTP_200_OK)

class UserListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskDataSerializer, DashboardAttendanceSerializer, TaskSerializer, AttendanceSerializer
from .models import Task, Attendance
from django.db.models import Count, Q
from django.utils import timezone
from django.db.models.functions import ExtractMonth

class DashboardTaskView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Fetch all tasks for the authenticated user
        tasks = Task.objects.filter(assigned_to=request.user).order_by('id')
        
        # Aggregate task summary
        task_summary = {
            'not_started': tasks.filter(status='Not Started').count(),
            'in_progress': tasks.filter(status='In Progress').count(),
            'completed': tasks.filter(status='Completed').count(),
            'awaiting_feedback': tasks.filter(status='Awaiting Feedback').count(),
        }

        # Prepare task data
        task_data = {
            'taskData': TaskSerializer(tasks, many=True).data,
            'taskSummary': task_summary,
        }

        serializer = TaskDataSerializer(task_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DashboardAttendanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Aggregate attendance data by month for the authenticated user
        today = timezone.now()
        attendance_data = Attendance.objects.filter(user=request.user, date__year=today.year).values('date').annotate(
            month=ExtractMonth('date')
        ).values(
            'month'
        ).annotate(
            present=Count('id', filter=Q(total_hours__gt=0)),  # Present if hours worked
            absent=Count('id', filter=Q(total_hours=0))  # Absent if no hours
        ).order_by('month')

        # Map month numbers to names and format data
        month_names = {
            1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
            7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
        }
        date_data = [
            {
                'month': month_names.get(row['month'], 'Unknown'),
                'present': row['present'],
                'absent': row['absent']
            } for row in attendance_data
        ]

        # Fill in missing months with 0s
        for month in range(1, 13):
            month_name = month_names[month]
            if not any(d['month'] == month_name for d in date_data):
                date_data.append({'month': month_name, 'present': 0, 'absent': 0})

        date_data.sort(key=lambda x: list(month_names.values()).index(x['month']))

        serializer = DashboardAttendanceSerializer({'dateData': date_data})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# views.py
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.paginator import Paginator
from django.db.models import Count
from .models import Customer, Candidate
from .serializers import CustomerSerializer

class CustomerListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 10))
        customers = Customer.objects.all().order_by('last_edit_date')
        paginator = Paginator(customers, per_page)
        page_obj = paginator.get_page(page)
        serializer = CustomerSerializer(page_obj, many=True)
        return Response({
            'customers': serializer.data,
            'total_pages': paginator.num_pages,
            'current_page': page,
            'total_entries': customers.count(),
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            customer = Customer.objects.get(pk=pk)
            serializer = CustomerSerializer(customer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            customer = Customer.objects.get(pk=pk)
            serializer = CustomerSerializer(customer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            customer = Customer.objects.get(pk=pk)
            customer.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

class CustomerSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        customers = Customer.objects.all()
        summary = {
            'active': customers.filter(status='Active').count(),
            'inactive': customers.filter(status='Inactive').count(),
            'sales_reps': CandidateSerializer(
                Candidate.objects.filter(designation__role="Sales Representative"),
                many=True
            ).data
        }
        return Response(summary, status=status.HTTP_200_OK)

class CustomerDuplicatesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Identify duplicates based on first_name and last_name
        duplicates = (
            Customer.objects.values('first_name', 'last_name')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )

        duplicate_groups = []
        for item in duplicates:
            first_name = item['first_name']
            last_name = item['last_name']
            matching_customers = Customer.objects.filter(first_name=first_name, last_name=last_name)
            if matching_customers.count() > 1:
                primary = matching_customers.order_by('last_edit_date').first()  # Use earliest last_edit_date as primary
                duplicates = matching_customers.exclude(id=primary.id)
                serializer = CustomerSerializer(primary)
                duplicates_serializer = CustomerSerializer(duplicates, many=True)
                group = {
                    'primary': serializer.data,
                    'duplicates': duplicates_serializer.data
                }
                duplicate_groups.append(group)

        return Response(duplicate_groups, status=status.HTTP_200_OK)

class CustomerMergeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        primary_id = request.data.get('primary_id')
        duplicate_ids = request.data.get('duplicate_ids', [])

        if not primary_id or not duplicate_ids:
            return Response(
                {'error': 'Primary ID and duplicate IDs are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            primary = Customer.objects.get(id=primary_id)
            duplicates = Customer.objects.filter(id__in=duplicate_ids)

            if not duplicates.exists():
                return Response(
                    {'error': 'No valid duplicates provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Merge logic: Keep primary record, delete duplicates
            serializer = CustomerSerializer(primary)
            duplicates.delete()

            return Response(
                {'merged_record': serializer.data},
                status=status.HTTP_200_OK
            )
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Primary record or duplicates not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
