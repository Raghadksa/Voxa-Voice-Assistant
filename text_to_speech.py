import os
import uuid

from gtts import gTTS


OUTPUT_FOLDER = "outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def detect_language(text: str) -> str:
    """
    Detect whether the response is mostly Arabic or English.
    """

    arabic_characters = sum(
        1 for character in text
        if "\u0600" <= character <= "\u06FF"
    )

    return "ar" if arabic_characters > 2 else "en"


def text_to_speech(text: str) -> str:
    """
    Convert text into an MP3 audio file.
    """

    if not text or not text.strip():
        raise ValueError("There is no text to convert into speech.")

    language = detect_language(text)
    file_name = f"response_{uuid.uuid4().hex}.mp3"
    output_path = os.path.join(OUTPUT_FOLDER, file_name)

    speech = gTTS(
        text=text,
        lang=language,
        slow=False,
    )

    speech.save(output_path)

    return output_path