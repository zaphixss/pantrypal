from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .gemini import ask_gemini

from .models import Conversation, Ingredient, Message, UserPreference
from .serializers import (
    ConversationSerializer,
    IngredientSerializer,
    MessageSerializer,
    UserPreferenceSerializer,
)



class ConversationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversations = Conversation.objects.filter(user=request.user).order_by('-updated_at')
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ConversationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class ConversationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        return get_object_or_404(Conversation, pk=pk, user=request.user)

    def get(self, request, pk):
        conversation = self.get_object(request, pk)
        return Response(ConversationSerializer(conversation).data)

    def put(self, request, pk):
        conversation = self.get_object(request, pk)
        serializer = ConversationSerializer(conversation, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data)

    def patch(self, request, pk):
        conversation = self.get_object(request, pk)
        serializer = ConversationSerializer(conversation, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data)

    def delete(self, request, pk):
        conversation = self.get_object(request, pk)
        conversation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ingredients = Ingredient.objects.filter(user=request.user).order_by('-created_at')
        serializer = IngredientSerializer(ingredients, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = IngredientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class IngredientDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        return get_object_or_404(Ingredient, pk=pk, user=request.user)

    def get(self, request, pk):
        ingredient = self.get_object(request, pk)
        return Response(IngredientSerializer(ingredient).data)

    def put(self, request, pk):
        ingredient = self.get_object(request, pk)
        serializer = IngredientSerializer(ingredient, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data)

    def patch(self, request, pk):
        ingredient = self.get_object(request, pk)
        serializer = IngredientSerializer(ingredient, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data)

    def delete(self, request, pk):
        ingredient = self.get_object(request, pk)
        ingredient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserPreferenceListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        preferences = UserPreference.objects.filter(user=request.user).order_by('-created_at')
        serializer = UserPreferenceSerializer(preferences, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserPreferenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserPreferenceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        return get_object_or_404(UserPreference, pk=pk, user=request.user)

    def get(self, request, pk):
        preference = self.get_object(request, pk)
        return Response(UserPreferenceSerializer(preference).data)

    def put(self, request, pk):
        preference = self.get_object(request, pk)
        serializer = UserPreferenceSerializer(preference, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data)

    def patch(self, request, pk):
        preference = self.get_object(request, pk)
        serializer = UserPreferenceSerializer(preference, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data)

    def delete(self, request, pk):
        preference = self.get_object(request, pk)
        preference.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SendMessageView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):

        # 1. Find conversation and make sure it belongs
        #    to the logged-in user
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
            user=request.user
        )


        if not Ingredient.objects.filter(user=request.user).exists() or not UserPreference.objects.filter(user=request.user).exists():
            return Response(
                {'detail': 'Add ingredients and preferences before chatting.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2. Validate the message from the frontend
        serializer = MessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 3. Save the user's new message
        Message.objects.create(
            conversation=conversation,
            role="user",
            content=serializer.validated_data["content"]
        )

        # 4. Get recent conversation history
        conversation_history = list(
            conversation.messages
            .order_by("-created_at")[:10]
        )

        # We fetched newest first.
        # Gemini should receive oldest → newest.
        conversation_history.reverse()

        # 5. Get saved preferences
        preferences = list(
            UserPreference.objects.filter(
                user=request.user
            )
        )

        ingredients = list(
            Ingredient.objects.filter(
                user=request.user
            )
        )

        # 6. Give Gemini everything it needs
        try:
            gemini_reply = ask_gemini(
                conversation_history=conversation_history,
                preferences=preferences,
                ingredients=ingredients
            )

        except Exception:
            return Response(
                {
                    "error": "PantryPal could not generate a response."
                },
                status=status.HTTP_502_BAD_GATEWAY
            )

        # 7. Save Gemini's response
        assistant_message = Message.objects.create(
            conversation=conversation,
            role="assistant",
            content=gemini_reply
        )

        # 8. Return Gemini's response
        return Response(
            {
                "conversation_id": conversation.id,
                "message": {
                    "id": assistant_message.id,
                    "role": assistant_message.role,
                    "content": assistant_message.content,
                    "created_at": assistant_message.created_at
                }
            },
            status=status.HTTP_201_CREATED
        )
