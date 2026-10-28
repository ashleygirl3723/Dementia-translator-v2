# Dementia Translator V2 — In the moment

No preset scenarios. No beginner prompt list.

Type whatever is happening right now — a behaviour, an action, a
sentence they said — in your own words. Add, optionally, the time of
day, what you already tried, whether safety is a concern, and whether
you want the words in Spanish with audio. You get back a thoughtful,
specific response for that case, built for an experienced caregiver:

- Likely signals, ranked, with what to watch for in the next 2 minutes
- Do first, in the next 60 seconds
- Say this, with an alternative line if the first does not land
- Avoid in this case, tied to this case
- If it does not settle, what next and when to get help
- Check urgently if, when relevant

What it does not do:
- It does not diagnose, read minds, or recommend medication.
- A sudden change, new pain, fever, a fall, or fast escalation should
  be checked with the care team promptly.
- Never enter resident names, photos, or health records. Nothing is saved.

## How it works

`dementia_v2.py` holds the prompt and the fallback, with no Streamlit
import, so it can be tested plainly. `app.py` is the Streamlit screen.
The model is called through OpenRouter (`openrouter/free`, the shared
free router used by the other apps here), so no new provider is needed.

## Deploy

1. Owner creates / reuses a public GitHub repo. This draft lives in
   `dementia-translator-v2/` locally; it is NOT pushed until the owner
   approves the exact files.
2. Deploy on share.streamlit.io: pick the repo, branch `main`, main
   file `app.py`.
3. In Streamlit Settings → Secrets, add:
   ```
   OPENROUTER_API_KEY = "your-key-here"
   ```
   Or paste a key in the sidebar for one visit only.
4. In the app dashboard, Settings → Sharing → Public, so it opens
   without a sign-in prompt.
5. Verify it opens, a free-form case returns a structured response,
   and Spanish audio plays if that box is ticked, before calling it live.

Files: `app.py`, `dementia_v2.py`, `requirements.txt`, `README.md`.
