from rest_framework import serializers
from .models import CustomUser
from rest_framework.authtoken.views import Token

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['name', 'username', 'email', 'password', 'phone', 'address', 'purpose', 'otherPurpose', 'profile_picture']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        purpose = validated_data.get('purpose', '')  # Get the purpose value from the validated data

        # If purpose is 'Other', use the value from 'otherPurpose' if provided
        if purpose == 'Other':
            other_purpose = validated_data.pop('otherPurpose', '')  # Retrieve otherPurpose if present
            validated_data['purpose'] = other_purpose if other_purpose else 'Other'
        # user = CustomUser(
        #     # name=validated_data['name'],
        #     username=validated_data['username'],
        #     email=validated_data['email'],
        #     # phone=validated_data['phone'],
        #     # address=validated_data['address'],
           
        # )
        # user.set_password(validated_data['password'])
        # user.save()
        user = CustomUser.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user
    

# from rest_framework import serializers

# class ChangePasswordSerializer(serializers.Serializer):
#     old_password = serializers.CharField(required=True)
#     new_password = serializers.CharField(required=True)

# class ResetPasswordEmailSerializer(serializers.Serializer):
#     email = serializers.EmailField(required=True)