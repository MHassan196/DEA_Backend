from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
# from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
# from django_otp.oath import TOTP
# from django_otp.util import random_hex
# # Generate and send OTP via Twilio
# from twilio.rest import Client

@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            username = serializer.validated_data.get('username')

            # Check if email or username already exists
            if CustomUser.objects.filter(email=email).exists():
                return Response({'email_exists': True}, status=status.HTTP_400_BAD_REQUEST)
            if CustomUser.objects.filter(username=username).exists():
                return Response({'username_exists': True}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

from .models import CustomUser

@api_view(['POST'])
def user_login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')

        user = None
        if '@' in username:
            try:
                user = CustomUser.objects.get(email=username)
            except ObjectDoesNotExist:
                pass

        if not user:
            user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'status': 'success','token': token.key}, status=status.HTTP_200_OK)

        return Response({'status': 'error','error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    if request.method == 'POST':
        try:
            # Delete the user's token to logout
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# accounts/views.py

# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import status
# from django.contrib.auth import update_session_auth_hash
# from .serializers import ChangePasswordSerializer

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def change_password(request):
#     if request.method == 'POST':
#         serializer = ChangePasswordSerializer(data=request.data)
#         if serializer.is_valid():
#             user = request.user
#             if user.check_password(serializer.data.get('old_password')):
#                 user.set_password(serializer.data.get('new_password'))
#                 user.save()
#                 update_session_auth_hash(request, user)  # To update session after password change
#                 return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
#             return Response({'error': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user  # Retrieve the authenticated user
    serializer = UserSerializer(user)  # Serialize the user data
    serialized_data = serializer.data
    # Include the user's ID in the serialized data
    serialized_data['id'] = user.id
    return Response(serialized_data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user_profile(request, id):
    user = request.user

    # Make sure the user making the request is the one being updated
    if user.id != id:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = UserSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)