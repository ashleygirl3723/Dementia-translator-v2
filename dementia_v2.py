"""Core logic for Dementia Translator V2.

No Streamlit import here, so this file can be tested plainly with Python.

V2 is deliberately NOT a preset scenario list. The caregiver types whatever
is happening right now, in their own words, and the model is asked for a
thoughtful, advanced response. The user is assumed to be an experienced
caregiver, so generic beginner advice is not the answer.
"""

SYSTEM_PROMPT = """You are an in-the-moment dementia-care thinking partner for an
experienced caregiver with many years on the job. Do NOT give beginner
advice as the main answer. Do not start with "be patient, speak slowly,
use simple words" and do not give a generic list that would fit any
situation. Assume the caregiver already knows the basics.

Work from the specific behaviour / action described, not from a
diagnosis. Think about, and rank, the most plausible drivers for THIS
case: an unmet physical need (pain, toileting, hunger, thirst, fatigue,
being too hot/cold), a sensory or environmental trigger (noise, crowding,
rush, a change in routine or person), a perceived threat or loss of
control, a preserved identity or life-history thread (work, family, a
place, a role), a communication mismatch (too many steps, a question
that feels like a test, being corrected), and a change from baseline.

Give a specific, dignity-preserving response, not a slogan. Be concrete
about body position, distance, tone, timing, and what to do if the first
move does not work. Offer exact words, short and calm, one idea at a
time. If a second line is needed when the first does not land, give it.

Never diagnose, never recommend a medication or dose, and never restrain
or argue a fact as a solution. If there is a sudden change, new pain,
fever, a fall, an injury, chest pain, trouble breathing, or a fast
escalation, say clearly: tell the nurse / care team promptly, do not
wait it out.

Use exactly these headings, in this order, and keep each section short
enough to read mid-shift:

## Likely signals
2-3 ranked possibilities for this case, with one sentence each on why
it fits and what you would notice in the next 2 minutes that would
support or rule it out. Do not list every possible cause.

## Do first, in the next 60 seconds
One specific first move, with timing and positioning. Not a list of
five things.

## Say this
Exact words to say, in quotes. Then, on a new line, one alternative
line if the first does not land. Keep each line to one idea.

## Avoid in this case
One or two specific things that would likely make THIS situation worse,
and why. Tie it to the case, do not give a generic do-not list.

## If it does not settle
What to try next, and after how long, and when to step back, get help,
or check a physical need in private (toilet, pain, hunger, rest) rather
than pushing through.

## Check urgently if
Only list this if it is relevant to the case. Sudden change, pain,
fever, fall, injury, or distress that is new or escalating means tell
the nurse promptly.
"""


def validate_input(behavior: str) -> str | None:
    """Return an error message, or None if the input is usable."""
    text = (behavior or "").strip()
    if len(text) < 10:
        return "Add a little more detail: what did they do or say, and where / when did it happen?"
    return None


def build_user_prompt(behavior: str, time_of_day: str = "",
                      already_tried: str = "", safety: bool = False,
                      spanish: bool = False) -> str:
    parts = [f"What is happening right now:\n{behavior.strip()}"]
    if time_of_day:
        parts.append(f"Time of day: {time_of_day}")
    if already_tried.strip():
        parts.append(
            "Already tried (do not simply repeat this, unless you explain "
            f"a different twist on it): {already_tried.strip()}"
        )
    if safety:
        parts.append(
            "Safety note: the caregiver is concerned this could escalate "
            "or someone could get hurt. Prioritise de-escalation, distance, "
            "and getting help early over completing the task."
        )
    parts.append(
        "Answer for an experienced caregiver. Be specific to this case, "
        "not generic. Use the headings in your instructions, in order."
    )
    if spanish:
        parts.append(
            "Also, after 'Say this', add a section headed '## Say this in Spanish' "
            "with the same lines translated into Spanish, using the respectful "
            "usted form for an older adult, short and calm. Do not add any other "
            "Spanish unless it is those lines."
        )
    return "\n\n".join(parts)


def fallback_response() -> str:
    """Shown only when the model cannot be reached.

    This is a thinking check, not a preset scenario, and it is not a
    substitute for the model response. It is here so the page is not
    useless offline mid-shift.
    """
    return """## Model not available right now

The thoughtful response could not be generated. Use this check, in order,
for the specific case in front of you:

1. **Body first, in private if possible:** toilet, pain, hunger, thirst,
   tired, too hot/cold, a wet or uncomfortable item of clothing.
2. **What changed in the last hour?** A new person, noise, rush, missed
   meal or rest, a room change, a task that felt like a test or a loss
   of control.
3. **What are they protecting?** A role, a place, a person, dignity
   during personal care. Name that, do not argue the fact.
4. **One move, then watch:** change one thing (distance, tone, who
   speaks, where you stand, give a choice of two), wait, and watch
   their face and body before you add another step.
5. **If it is sudden, new pain, fever, a fall, or escalating fast:**
   tell the nurse promptly, do not wait it out.

Do not enter resident names, photos, or health records here. Nothing
on this page is saved.
"""


def extract_spanish_lines(response: str) -> list[str]:
    """Pull the Spanish 'Say this' lines out of a model response, if any."""
    lines: list[str] = []
    in_spanish = False
    for raw in response.splitlines():
        line = raw.strip()
        if line.lower().startswith("## say this in spanish"):
            in_spanish = True
            continue
        if in_spanish and line.startswith("##"):
            break
        if in_spanish and line:
            # Strip quotes, bullets, and numbering, keep the sentence.
            cleaned = line.strip('">•-* ').strip()
            cleaned = cleaned.strip('"“”')
            if cleaned and len(cleaned) > 3:
                lines.append(cleaned)
    return lines[:4]
