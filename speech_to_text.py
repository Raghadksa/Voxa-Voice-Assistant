from faster_whisper import WhisperModel


model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8",
)


def speech_to_text(audio_path: str) -> str:
    """
    Convert recorded speech into text using Faster-Whisper.
    """

    if not audio_path:
        raise ValueError("No audio was provided.")

    segments, _ = model.transcribe(
        audio_path,
        beam_size=5,
        vad_filter=True,
    )

    transcript_parts = [
        segment.text.strip()
        for segment in segments
        if segment.text.strip()
    ]

    return " ".join(transcript_parts)