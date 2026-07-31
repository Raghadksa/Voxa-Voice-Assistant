import os

import cohere
from dotenv import load_dotenv


# Load variables from the .env file
load_dotenv()

API_KEY = os.getenv("COHERE_API_KEY")

if not API_KEY:
    raise ValueError(
        "COHERE_API_KEY was not found. "
        "Please add it to the .env file."
    )


client = cohere.ClientV2(api_key=API_KEY)


def detect_language(text: str) -> str:
    """
    Detect whether the user's message is Arabic or English.
    """

    arabic_count = sum(
        1
        for character in text
        if "\u0600" <= character <= "\u06FF"
    )

    english_count = sum(
        1
        for character in text
        if character.isascii() and character.isalpha()
    )

    if arabic_count >= english_count:
        return "ar"

    return "en"


def extract_response_text(response) -> str:
    """
    Extract only the text content from Cohere's response.
    """

    for item in response.message.content:
        if getattr(item, "type", None) == "text":
            text = getattr(item, "text", None)

            if text:
                return text.strip()

    raise ValueError("No text response was returned by Cohere.")


def generate_ai_response(user_text: str) -> str:
    """
    Generate a bilingual Arabic or English response using Cohere.
    """

    if not user_text or not user_text.strip():
        return "I can not understand, please try again"

    user_text = user_text.strip()
    language = detect_language(user_text)

    if language == "ar":
        language_instruction = (
            "The user's message is Arabic. "
            "Reply only in natural Arabic. "
            "Do not use English, Vietnamese, or any other language."
        )
    else:
        language_instruction = (
            "The user's message is English. "
            "Reply only in natural English. "
            "Do not use Arabic, Vietnamese, or any other language."
        )

    try:
        response = client.chat(
            model="command-a-plus-05-2026",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are NOVA, a professional bilingual voice "
                        "assistant that supports Arabic and English. "
                        f"{language_instruction} "
                        "Keep the answer helpful, friendly, clear, and short "
                        "because it will be converted into speech."
                    ),
                },
                {
                    "role": "user",
                    "content": user_text,
                },
            ],
            max_tokens=300,
            temperature=0.3,
        )

        response_text = extract_response_text(response)

        # Extra language validation
        response_language = detect_language(response_text)

        if response_language != language:
            correction_response = client.chat(
                model="command-a-plus-05-2026",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Rewrite the following answer only in Arabic."
                            if language == "ar"
                            else
                            "Rewrite the following answer only in English."
                        ),
                    },
                    {
                        "role": "user",
                        "content": response_text,
                    },
                ],
                max_tokens=300,
                temperature=0.1,
            )

            response_text = extract_response_text(
                correction_response
            )

        return response_text

    except Exception as error:
        return f"AI service error: {error}"