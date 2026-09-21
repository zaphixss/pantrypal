from rest_framework import serializers

from .models import Conversation, Message, UserPreference


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ('id', 'user', 'title', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'conversation', 'role', 'content', 'created_at')
        read_only_fields = ('id', 'created_at')


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ('id', 'user', 'title', 'preference_type', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')
