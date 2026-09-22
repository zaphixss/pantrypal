from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()


def ask_gemini(conversation_history, preferences, ingredients):

    # Turn preferences into simple text
    preference_text = ", ".join(
        f"{preference.preference_type}: {preference.title}"
        for preference in preferences
    )

    # Turn conversation history into simple text
    conversation_text = "\n".join(
        f"{message.role}: {message.content}"
        for message in conversation_history
    )


    ingredients_text = "\n".join(
        f"""- {ingredient.title}
            Quantity: {ingredient.quantity}
            Description: {ingredient.description}
            Purchase date: {ingredient.purchase_date}
            Expiry date: {ingredient.expiry_date}
        """
        for ingredient in ingredients
    )

    # Everything Gemini needs
    prompt = f"""
    You are PantryPal, a conversational cooking assistant.

    Your job is to help the user decide what to cook based primarily on:
    1. Their saved ingredients
    2. Their saved food preferences
    3. The current conversation

    The user's ingredients and preferences have already been saved in the application.
    Do not ask the user to provide them again if they are available below.

    Saved preferences:
    {preference_text or "No saved preferences."}

    Available ingredients:
    {ingredients_text or "No saved ingredients."}

    Conversation so far:
    {conversation_text or "No previous conversation."}

    Rules:
    - Talk naturally and keep the conversation friendly and simple.
    - Use the user's available ingredients when suggesting meals.
    - Respect all saved dietary preferences and disliked ingredients.
    - Do not suggest meals that strongly depend on ingredients the user does not have.
    - If a meal requires a small extra ingredient, clearly tell the user what is missing.
    - If some ingredients are close to their expiry date, prioritize meals that use them.
    - If the user asks what they can cook, check their saved ingredients and preferences automatically.
    - Do not ask unnecessary questions when enough information is already available.
    - If important information is genuinely missing, ask a short follow-up question.
    - Remember the previous conversation when responding to follow-up requests such as
    "make it healthier", "make it faster", or "I don't like the second option".
    - Do not invent ingredients that are not in the user's available ingredients.
    - Give practical meal suggestions the user can realistically make.

    Continue the conversation as PantryPal.

    """

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    return response.text
