import hashlib
import io

import streamlit as st
import streamlit.components.v1 as components

from dementia_v2 import (
    SYSTEM_PROMPT,
    build_user_prompt,
    extract_spanish_lines,
    fallback_response,
    validate_input,
)

st.set_page_config(
    page_title="Dementia Translator — In the moment",
    page_icon="💬",
    layout="centered",
)

st.title("💬 Dementia Translator")
st.write(
    "No preset scenarios. Describe what is happening right now, in your "
    "own words, and get a thoughtful, specific response for this case. "
    "This is for an experienced caregiver — it skips the beginner basics "
    "and goes straight to what is likely driving this moment and what "
    "to do next."
)
st.info(
    "Communication aid only. It does not diagnose, it does not recommend "
    "medication, and it does not replace the nurse or care team. A sudden "
    "change, new pain, fever, a fall, or fast escalation should be checked "
    "with the care team promptly. Never enter resident names, photos, or "
    "health records here. Nothing you type is saved."
)

# --- API key: Streamlit secrets first, sidebar second, never in code ---
api_key = ""
try:
    api_key = st.secrets.get("OPENROUTER_API_KEY", "")
except Exception:
    api_key = ""
if not api_key:
    with st.sidebar:
        st.write("Model key")
        api_key = st.text_input(
            "OpenRouter API key (this visit only, not saved)",
            type="password",
            help="Add OPENROUTER_API_KEY in Streamlit Settings → Secrets for the deployed app, or paste it here for this visit.",
        )
        st.caption("Model: openrouter/free, the shared free router used by the other apps here.")

# --- The one input that matters ---
behavior = st.text_area(
    "What is happening right now?",
    height=140,
    placeholder=(
        "Example, in your own words: She keeps trying to leave through the "
        "front door during shift change, says someone is waiting for her, "
        "and pushed my hand away when I tried to guide her back."
    ),
    help="What they did or said, where, and what changed just before it. The more specific you are, the less generic the answer will be.",
)

col1, col2 = st.columns(2)
with col1:
    time_of_day = st.selectbox(
        "Time of day (optional)",
        ["", "Morning", "Afternoon", "Evening", "Night"],
    )
    safety = st.checkbox("Safety / escalation concern")
with col2:
    already_tried = st.text_input(
        "Already tried? (optional)",
        placeholder="e.g. offered a walk, tried redirecting to tea",
    )
    spanish = st.checkbox("Also give the words in Spanish, with audio")

if st.button("Get a thoughtful response", type="primary"):
    err = validate_input(behavior)
    if err:
        st.warning(err)
    elif not api_key:
        st.warning(
            "No model key yet. Add OPENROUTER_API_KEY in Streamlit Secrets, "
            "or paste it in the sidebar for this visit."
        )
        st.markdown(fallback_response())
    else:
        with st.spinner("Thinking about this specific case…"):
            try:
                from openai import OpenAI

                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key,
                )
                resp = client.chat.completions.create(
                    model="openrouter/free",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": build_user_prompt(
                                behavior, time_of_day, already_tried, safety, spanish
                            ),
                        },
                    ],
                    temperature=0.7,
                )
                answer = resp.choices[0].message.content or ""
            except Exception as e:
                st.warning(f"Model call failed: {e}")
                answer = ""
        if answer:
            st.markdown(answer)
            if spanish:
                es_lines = extract_spanish_lines(answer)
                if es_lines:
                    st.subheader("🔊 Spanish audio")
                    st.write("Play it once, watch their face, play it again if needed.")
                    for line in es_lines:
                        st.write(f"🇪🇸 {line}")
                        # gTTS on demand, cached for this visit
                        cache_key = "gtts_" + hashlib.md5(line.encode("utf-8")).hexdigest()
                        if cache_key not in st.session_state:
                            try:
                                from gtts import gTTS

                                buf = io.BytesIO()
                                gTTS(text=line, lang="es").write_to_fp(buf)
                                st.session_state[cache_key] = buf.getvalue()
                            except Exception:
                                st.session_state[cache_key] = None
                        if st.session_state.get(cache_key):
                            st.audio(st.session_state[cache_key], format="audio/mp3")
                        # Phone-voice fallback, same as V1
                        uid = hashlib.md5(line.encode("utf-8")).hexdigest()[:10]
                        import json

                        html_code = f"""
                        <button onclick="speak_{uid}()" style="font-size:18px;padding:10px 16px;border-radius:12px;border:1px solid #ccc;background:#ffffff;cursor:pointer;">🔊 Play with phone voice</button>
                        <script>
                        function speak_{uid}() {{
                          if (!('speechSynthesis' in window)) {{ alert('This device does not support spoken audio.'); return; }}
                          window.speechSynthesis.cancel();
                          var u = new SpeechSynthesisUtterance({json.dumps(line)});
                          u.lang = 'es-MX';
                          u.rate = 0.8;
                          var voices = window.speechSynthesis.getVoices();
                          var v = voices.find(function(v) {{ return v.lang && v.lang.toLowerCase().startsWith('es'); }});
                          if (v) {{ u.voice = v; }}
                          window.speechSynthesis.speak(u);
                        }}
                        </script>
                        """
                        components.html(html_code, height=60)
        else:
            st.markdown(fallback_response())

st.divider()
st.caption(
    "V2: free-form only, no preset scenarios, no beginner prompt list. "
    "Type a behaviour, an action, or a situation — the response is built "
    "for that case. Advanced, specific, and mid-shift short. Nothing is saved."
)
