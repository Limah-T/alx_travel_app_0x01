from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from .serializers import PropertySerializer, BookingSerializer
from .auth import UserSerializer, LoginSerializer
from .models import Property, Booking, User

class UserViewset(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = []
    http_method_names = ["get", "post", "patch", "put", "delete"]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        print(serializer.data)
        return Response(serializer.data)
    
class LoginViewset(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = []
    http_method_names = ["post"]
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        user = authenticate(email=email, password=password)
        print(user)
        if not user:
            return Response({'error': 'Unable to log in with the provided credentials'}, status=status.HTTP_400_BAD_REQUEST)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)

class PropertyViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "put", "delete"]
    serializer_class = PropertySerializer
    queryset = Property.objects.select_related('user').all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        name = serializer.validated_data.get('name')
        description = serializer.validated_data.get('description')
        location = serializer.validated_data.get('location')
        pricepernight = serializer.validated_data.get('pricepernight')
        property = Property.objects.create(
                                user=user, name=name,
                                description=description, 
                                location=location, pricepernight=pricepernight
                            )
        serializer = self.get_serializer(property)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        print(request.user.role)
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        print(kwargs.get('pk'))
        property = get_object_or_404(Property, property_id=kwargs.get('pk'))
        serializer = self.get_serializer(property)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        property = get_object_or_404(Property, property_id=kwargs.get('pk'))
        serializer = self.get_serializer(data=request.data, instance=property, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = self.get_serializer(property)
        return Response(data=serializer.data, status=status.HTTP_202_ACCEPTED)
    
    def destroy(self, request, *args, **kwargs):
        property = get_object_or_404(Property, property_id=kwargs.get('pk'))
        property.delete()
        return Response({'success': 'Successfully deleted the property'}, status=status.HTTP_200_OK)
    
class BookingViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "put", "delete"]
    serializer_class = BookingSerializer
    queryset = Booking.objects.select_related('user', 'property_id').all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        property = serializer.validated_data.get('property_id')
        user = request.user
        start_date = serializer.validated_data.get('start_date')
        end_date = serializer.validated_data.get('end_date')
        booking = Booking.objects.create(property_id=property.property_id,
                                        user=user, start_date=start_date,
                                        end_date=end_date, total_price=property.pricepernight)
        serializer = self.get_serializer(booking)
        return Response({'success': 'Successfully booked a property',
                        'data': serializer.data
                        }, status=status.HTTP_201_CREATED)
        
    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        booking = get_object_or_404(Booking, booking_id=kwargs.get('pk'))
        serializer = self.get_serializer(data=request.data, instance=booking, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = self.get_serializer(booking)
        return Response({'success': 'Successfully updated a booking',
                        'data':serializer.data}, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, *args, **kwargs):
        booking = get_object_or_404(Booking, booking_id=kwargs.get('pk'))
        booking.delete()
        return Response({'success': 'Successfully deleted the booking'}, status=status.HTTP_200_OK)
