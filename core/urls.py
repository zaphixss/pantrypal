from django.urls import path

from .views import (
    ConversationDetailView,
    ConversationListCreateView,
    IngredientDetailView,
    IngredientListCreateView,
    UserPreferenceDetailView,
    UserPreferenceListCreateView,
    SendMessageView
)


urlpatterns = [
    path('conversations/', ConversationListCreateView.as_view(), name='conversation-list-create'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<int:conversation_id>/messages/', SendMessageView.as_view(), name='send-message',),
    path('ingredients/', IngredientListCreateView.as_view(), name='ingredient-list-create'),
    path('ingredients/<int:pk>/', IngredientDetailView.as_view(), name='ingredient-detail'),
    path('preferences/', UserPreferenceListCreateView.as_view(), name='preference-list-create'),
    path('preferences/<int:pk>/', UserPreferenceDetailView.as_view(), name='preference-detail'),
]
