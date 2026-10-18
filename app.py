import streamlit as st

from config import (
    AVAILABLE_MODELS,
    DEFAULT_IMAGE_PROMPT,
    MAX_HISTORY_MESSAGES,
    MAX_IMAGES_PER_MESSAGE,
    OPENAI_KEY,
)
from core.image_utils import process_and_encode_image
from core.multimodal_client import MultimodalClient

st.set_page_config(page_title="Multimodal AI Chatbot", page_icon="👁️", layout="centered")



st.markdown(
    """
    <style>
        /* Hide the top toolbar */
        [data-testid="stToolbar"] {
            display: none !important;
        }

        /* Hide the header decoration */
        [data-testid="stDecoration"] {
            display: none !important;
        }

        /* Hide Streamlit footer and bottom branding */
        footer {
            display: none !important;
        }

        [data-testid="stStatusWidget"] {
            display: none !important;
        }

        /* Hide the bottom-right deploy button */
        [data-testid="stAppDeployButton"] {
            display: none !important;
        }

        /* Hide the bottom app creator/branding area */
        .viewerBadge_container__1QSob,
        .styles_viewerBadge__1yB5q,
        .viewerBadge_link__1S137,
        [class*="viewerBadge"],
        [class*="ViewerBadge"] {
            display: none !important;
            visibility: hidden !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# # Hide Streamlit's default toolbar, footer and header
# st.markdown(
#     """
#     <style>
#         /* Hide the top-right toolbar, including Fork and GitHub */
#         [data-testid="stToolbar"] {
#             visibility: hidden;
#             height: 0%;
#             position: fixed;
#         }

#         /* Hide the footer */
#         footer {
#             visibility: hidden;
#         }

#         /* Hide Streamlit's header */
#         [data-testid="stHeader"] {
#             background: rgba(0, 0, 0, 0);
#         }

#         /* Hide the bottom-right status/decoration area */
#         [data-testid="stStatusWidget"] {
#             visibility: hidden;
#         }

#         /* Hide deploy button, if present */
#         .stDeployButton {
#             display: none;
#         }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )


if "messages" not in st.session_state:
    st.session_state.messages = []

def parse_chat_input(value):
    if isinstance(value, str):
        return value.strip(), []
    return (value.get("text") or "").strip(), list(value.get("files") or [])

def build_api_messages(history, supports_vision):
    window = history[-MAX_HISTORY_MESSAGES:]
    while window and window[0]["role"] == "assistant":  # never start on a reply
        window = window[1:]

    messages = []
    for msg in window:
        images = msg["images"] if supports_vision else []

        if images:
            content = [{"type": "text", "text": msg["text"] or DEFAULT_IMAGE_PROMPT}]
            content += [{"type": "image_url", "image_url": {"url": u}} for u in images]
        else:
            content = msg["text"]

        if content:
            messages.append({"role": msg["role"], "content": content})
    return messages

def render_message(msg):
    with st.chat_message(msg["role"]):
        if msg["text"]:
            st.markdown(msg["text"])
        for uri in msg["images"]:
            st.image(uri, width=250)

with st.sidebar:
    st.title("⚙️ Configuration")

    api_key = OPENAI_KEY

    selected_model_name = st.selectbox("Model", list(AVAILABLE_MODELS.keys()))
    current_model = AVAILABLE_MODELS[selected_model_name]

    temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.title("Multimodal AI Chatbot")
st.markdown("Upload images, ask questions, and test different models.")

if not api_key:
    st.warning("OpenAI API Key not configured.")
    st.stop()

try:
    client = MultimodalClient(api_key=api_key)
except ValueError as e:
    st.error(str(e))
    st.stop()

for msg in st.session_state.messages:
    render_message(msg)

supports_vision = current_model["supports_vision"]

user_input = st.chat_input(
    "Ask about an image..." if supports_vision else "Type a message...",
    accept_file="multiple" if supports_vision else False,
    file_type=["png", "jpg", "jpeg", "webp", "gif"] if supports_vision else None,
)

if user_input:
    prompt_text, uploaded_files = parse_chat_input(user_input)
    if not prompt_text and not uploaded_files:
        st.stop()

    if len(uploaded_files) > MAX_IMAGES_PER_MESSAGE:
        st.warning(f"Only the first {MAX_IMAGES_PER_MESSAGE} images were used.")
        uploaded_files = uploaded_files[:MAX_IMAGES_PER_MESSAGE]

    try:
        images = [process_and_encode_image(f.getvalue()) for f in uploaded_files]
    except ValueError as e:
        st.error(f"Image processing error: {e}")
        st.stop()
    user_msg = {"role": "user", "text": prompt_text, "images": images}
    render_message(user_msg)
    
    api_messages = build_api_messages(
        st.session_state.messages + [user_msg], supports_vision
    )

    with st.chat_message("assistant"):
        try:
            answer = st.write_stream(
                client.stream_response(
                    model_id=current_model["id"],
                    messages=api_messages,
                    temperature=temperature,
                )
            )
        except Exception as e:
            st.error(f"API Error: {e}. Your message was not saved, please resend.")
        else:
            st.session_state.messages.append(user_msg)
            st.session_state.messages.append(
                {"role": "assistant", "text": answer, "images": []}
            )
