import math
import streamlit as st
from learning_log import record_event, show_log

st.set_page_config(page_title="Sharing Detectives", page_icon="🧩")

TASKS = [
    {"groups": [4, 6, 8], "answer": 6},
    {"groups": [2, 4, 9], "answer": 5},
]
NAMES = ["Alex", "Sam", "Jo"]

# These settings belong only to this version of the app.
if "child_task" not in st.session_state:
    st.session_state.child_task = 0
    st.session_state.child_groups = TASKS[0]["groups"].copy()
    st.session_state.child_visual = False
    st.session_state.child_correct = False
    st.session_state.child_reason = False
    st.session_state.child_message = ""

s = st.session_state
task = TASKS[s.child_task]
task_id = s.child_task

st.title("🧩 Sharing Detectives")
st.write("Help three friends share their blocks equally.")
st.caption("Early demo: prepared questions and feedback. AI is not connected.")

st.subheader(f"Challenge {task_id + 1}")
starting = task["groups"]
st.write(
    f"Alex has **{starting[0]}** blocks, "
    f"Sam has **{starting[1]}**, and Jo has **{starting[2]}**."
)
st.write("Keep all the blocks. Share them so everyone has the same number.")

if not s.child_correct:
    with st.form(f"child_answer_{task_id}", clear_on_submit=True):
        answer = st.text_input("How many blocks should each friend have?")
        confidence = st.select_slider(
            "How sure do you feel?",
            options=["Not sure yet", "A little sure", "Very sure"],
            value="A little sure",
        )
        check = st.form_submit_button("Check my answer")

    if check:
        try:
            number = float(answer.strip())
            if not math.isfinite(number):
                raise ValueError
        except ValueError:
            s.child_message = "Please type a number."
        else:
            record_event(
                "answer_submitted",
                answer=number,
                confidence=confidence,
                correct=number == task["answer"],
                visual_help_used=s.child_visual,
            )
            if number == task["answer"]:
                s.child_correct = True
                s.child_message = ""
                st.balloons()
                st.rerun()
            else:
                s.child_visual = True
                if confidence == "Very sure":
                    s.child_message = (
                        "Let's check your idea with blocks. "
                        "Can everyone have the same number?"
                    )
                else:
                    s.child_message = (
                        "Let's explore together! Move one block at a time "
                        "until everyone has the same number."
                    )

    if s.child_message:
        st.info(s.child_message)

# Visual help appears after an incorrect answer.
if s.child_visual and not s.child_correct:
    st.subheader("Try sharing the blocks")
    st.write("Each blue square is one block.")

    for column, name, count in zip(
        st.columns(3), NAMES, s.child_groups
    ):
        with column:
            st.markdown(f"### {name}")
            st.write(f"{count} blocks")
            # Draw exact quantities in rows of five.
            if count == 0:
                st.write("No blocks")
            for start in range(0, count, 5):
                st.write("🟦 " * min(5, count - start))

    st.caption(f"Total blocks: {sum(s.child_groups)}")

    source = st.selectbox(
        "Take one block from",
        NAMES,
        index=2,
        key=f"child_from_{task_id}",
    )
    target = st.selectbox(
        "Give it to",
        NAMES,
        index=0,
        key=f"child_to_{task_id}",
    )

    if st.button("Move one block"):
        a, b = NAMES.index(source), NAMES.index(target)
        if a == b:
            st.warning("Choose two different friends.")
        elif s.child_groups[a] == 0:
            st.warning(f"{source} has no blocks to give.")
        else:
            before = s.child_groups.copy()
            s.child_groups[a] -= 1
            s.child_groups[b] += 1
            record_event(
                "block_moved",
                source=source,
                target=target,
                before=before,
                after=s.child_groups.copy(),
            )
            st.rerun()

    if len(set(s.child_groups)) == 1:
        st.success(
            "Everyone has the same number! "
            "Count one friend's blocks, then enter your answer above."
        )

# Ask for reasoning after every correct numerical answer.
if s.child_correct:
    st.success("🌟 You did it! Your number is correct.")
    st.subheader("Now, tell me why")

    with st.form(f"child_reason_{task_id}"):
        reason = st.radio(
            "Which explanation makes sense?",
            [
                "I used the biggest starting group.",
                "I shared all the blocks equally among the three friends.",
                "I counted only Alex's starting blocks.",
            ],
            index=None,
        )
        check_reason = st.form_submit_button("Check my explanation")

    if check_reason:
        if reason is not None:
            record_event(
                "explanation_submitted",
                explanation=reason,
                correct=reason == (
                    "I shared all the blocks equally among the three friends."
                ),
            )
        if reason is None:
            st.info("Choose an explanation first.")
        elif reason == (
            "I shared all the blocks equally among the three friends."
        ):
            s.child_reason = True
        else:
            s.child_reason = False
            st.info(
                "Think about both parts: keeping all the blocks "
                "and giving each friend the same number."
            )

    if s.child_reason:
        total = sum(task["groups"])
        st.success(
            f"Yes! {total} blocks shared equally among 3 friends "
            f"gives {task['answer']} each. That equal share is the mean."
        )

        if task_id + 1 < len(TASKS):
            if st.button("Try a new challenge"):
                s.child_task += 1
                s.child_groups = TASKS[s.child_task]["groups"].copy()
                s.child_visual = False
                s.child_correct = False
                s.child_reason = False
                s.child_message = ""
                st.rerun()
        else:
            st.success("You finished both challenges! ⭐")


show_log()
