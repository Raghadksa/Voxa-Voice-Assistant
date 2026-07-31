import gradio as gr

from llm_service import generate_ai_response
from speech_to_text import speech_to_text
from text_to_speech import text_to_speech


def process_voice(audio_path):
    """
    Run the complete voice-to-voice pipeline:
    Audio -> Text -> AI Response -> Spoken Response
    """

    if audio_path is None:
        return (
            "No recording received.",
            "Please record your voice before sending.",
            None,
            "Waiting for a recording...",
        )

    try:
        transcript = speech_to_text(audio_path)

        if not transcript:
            return (
                "No speech detected.",
                "I could not understand the recording. Please try again.",
                None,
                "No clear speech was detected.",
            )

        ai_response = generate_ai_response(transcript)

        if ai_response.startswith("AI service error:"):
            return (
                transcript,
                ai_response,
                None,
                "The AI service returned an error.",
            )

        response_audio = text_to_speech(ai_response)

        return (
            transcript,
            ai_response,
            response_audio,
            "Response generated successfully.",
        )

    except Exception as error:
        return (
            "",
            f"Error: {error}",
            None,
            "Something went wrong. Please check the error message.",
        )


def clear_interface():
    """
    Clear all interface components.
    """

    return (
        None,
        "",
        "",
        None,
        "Ready to listen.",
    )


CUSTOM_CSS = """
.gradio-container {
    max-width: 1150px !important;
    margin: auto !important;
    min-height: 100vh;
    background:
        radial-gradient(circle at top left, #492b7c 0%, transparent 32%),
        radial-gradient(circle at top right, #123d66 0%, transparent 30%),
        linear-gradient(135deg, #080b16 0%, #11172b 55%, #080d1b 100%);
}

.voxa-header {
    text-align: center;
    padding: 38px 15px 22px;
}

.voxa-logo {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 78px;
    height: 78px;
    margin-bottom: 12px;
    border-radius: 24px;
    font-size: 38px;
    background: linear-gradient(135deg, #8b5cf6, #38bdf8);
    box-shadow: 0 15px 40px rgba(86, 116, 255, 0.35);
}

.voxa-header h1 {
    margin: 0;
    font-size: 52px;
    font-weight: 800;
    letter-spacing: 1px;
    background: linear-gradient(90deg, #c7b8ff, #71ddff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.voxa-header h2 {
    margin-top: 8px;
    margin-bottom: 5px;
    font-size: 20px;
    color: #e2e8f0;
}

.voxa-header p {
    margin: 0;
    font-size: 15px;
    color: #aeb8d4;
}

.voxa-card {
    padding: 20px !important;
    border: 1px solid rgba(173, 188, 255, 0.18) !important;
    border-radius: 24px !important;
    background: rgba(17, 24, 48, 0.76) !important;
    box-shadow: 0 20px 45px rgba(0, 0, 0, 0.24);
    backdrop-filter: blur(16px);
}

.status-box {
    border: 1px solid rgba(130, 159, 255, 0.25) !important;
    border-radius: 16px !important;
    background: rgba(255, 255, 255, 0.05) !important;
}

.primary-button {
    min-height: 50px !important;
    border-radius: 15px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
}

.secondary-button {
    min-height: 50px !important;
    border-radius: 15px !important;
    font-size: 15px !important;
}

.pipeline-text {
    text-align: center;
    color: #98a4c3;
    padding-top: 10px;
}

footer {
    display: none !important;
}
"""


with gr.Blocks(
    title="Voxa Voice Assistant",
    css=CUSTOM_CSS,
    theme=gr.themes.Soft(
        primary_hue="violet",
        secondary_hue="sky",
        neutral_hue="slate",
    ),
) as demo:

    gr.HTML(
        """
        <div class="voxa-header">
            <div class="voxa-logo">🎙️</div>

            <h1>Voxa</h1>

            <h2>Your Intelligent Voice-to-Voice AI Assistant</h2>

            <p>
                Speak naturally. Think instantly. Respond intelligently.
            </p>
        </div>
        """
    )

    status_output = gr.Textbox(
        value="Ready to listen.",
        label="System Status",
        interactive=False,
        elem_classes=["status-box"],
    )

    with gr.Row():

        with gr.Column(
            scale=1,
            elem_classes=["voxa-card"],
        ):
            gr.Markdown("## Speak to Voxa")

            audio_input = gr.Audio(
                sources=["microphone", "upload"],
                type="filepath",
                label="Record or Upload Audio",
            )

            with gr.Row():

                send_button = gr.Button(
                    "Generate AI Response",
                    variant="primary",
                    elem_classes=["primary-button"],
                )

                clear_button = gr.Button(
                    "Clear",
                    variant="secondary",
                    elem_classes=["secondary-button"],
                )

        with gr.Column(
            scale=1,
            elem_classes=["voxa-card"],
        ):
            gr.Markdown("## Conversation")

            transcript_output = gr.Textbox(
                label="Your Message",
                placeholder="Your speech will appear here...",
                lines=4,
                interactive=False,
            )

            response_output = gr.Textbox(
                label="Voxa Response",
                placeholder="Voxa's response will appear here...",
                lines=7,
                interactive=False,
            )

            audio_output = gr.Audio(
                label="Spoken AI Response",
                autoplay=True,
                interactive=False,
            )

    gr.HTML(
        """
        <div class="pipeline-text">
            Microphone → Faster-Whisper → Cohere AI → gTTS
        </div>
        """
    )

    send_button.click(
        fn=process_voice,
        inputs=audio_input,
        outputs=[
            transcript_output,
            response_output,
            audio_output,
            status_output,
        ],
    )

    clear_button.click(
        fn=clear_interface,
        inputs=[],
        outputs=[
            audio_input,
            transcript_output,
            response_output,
            audio_output,
            status_output,
        ],
    )


if __name__ == "__main__":
    demo.launch(
        inbrowser=True,
        show_error=True,
    )