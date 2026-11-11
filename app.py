import math
import streamlit as st

st.set_page_config(page_title="Adaptive Learning Agent", page_icon="📚")
st.title("Adaptive Learning Agent")
st.caption("An early prototype by Farzana Fahmee")
st.info("Demo: basic statistics. Prepared tasks and rules; AI is not connected yet.")

# Store information between button clicks.
defaults = {
    "learning_goal": "",
    "feedback": None,
    "followup": None,
    "show_followup": False,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

with st.form("goal_form"):
    goal = st.text_input(
        "What would you like to learn?",
        value="I want to learn how to interpret basic statistics."
    )
    start = st.form_submit_button("Start learning")

if start:
    if goal.strip():
        st.session_state.learning_goal = goal.strip()
        st.session_state.feedback = None
        st.session_state.followup = None
        st.session_state.show_followup = False
    else:
        st.warning("Please enter a learning goal.")

if st.session_state.learning_goal:
    st.write("**Your goal:**", st.session_state.learning_goal)
    st.subheader("Practice 1: Calculate the mean")
    st.write("Three learners scored **4, 6, and 8** on a quiz.")

    with st.form("answer_form"):
        answer = st.text_input("What is their mean score?")
        confidence = st.slider(
            "How confident are you that your answer is correct?",
            0, 100, 50, step=10, format="%d%%"
        )
        submitted = st.form_submit_button("Check my answer")

    if submitted:
        try:
            number = float(answer.strip())
            if not math.isfinite(number):
                raise ValueError
        except ValueError:
            st.warning("Please enter a finite number, such as 6.")
            st.session_state.feedback = None
            st.session_state.followup = None
            st.session_state.show_followup = False
        else:
            correct = number == 6
            high_confidence = confidence >= 70

            if correct and not high_confidence:
                message = "Correct. Let's check the reasoning behind your answer."
                task = (
                    "We divide the total by the number of scores. "
                    "How many scores are in 4, 6, and 8?",
                    3,
                    "There are three scores, so the total is divided by 3."
                )
            elif correct and high_confidence:
                message = "Correct. Let's try a different set of scores."
                task = (
                    "What is the mean of 5, 7, and 12?",
                    8,
                    "The total is 24. There are three scores: 24 / 3 = 8."
                )
            elif not correct and high_confidence:
                message = "Not correct yet. Let's check which divisor to use."
                task = (
                    "The total of 4, 6, and 8 is 18. "
                    "What number should you divide 18 by to find the mean?",
                    3,
                    "Divide by 3 because there are three scores."
                )
            else:
                message = "Not correct yet. Let's begin with a smaller step."
                task = (
                    "What is 4 + 6 + 8?",
                    18,
                    "4 + 6 = 10, and 10 + 8 = 18."
                )

            st.session_state.feedback = (correct, message)
            st.session_state.followup = task
            st.session_state.show_followup = False

    if st.session_state.feedback is not None:
        correct, message = st.session_state.feedback
        if correct:
            st.success(message)
        else:
            st.warning(message)

        if st.button("Show my next task"):
            st.session_state.show_followup = True

    if st.session_state.show_followup:
        question, expected, explanation = st.session_state.followup
        st.subheader("Your follow-up task")
        st.write(question)

        # A different question gets a fresh answer box.
        with st.form("followup_" + question):
            followup_answer = st.text_input("Your answer")
            check_followup = st.form_submit_button("Check follow-up")

        if check_followup:
            try:
                number = float(followup_answer.strip())
                if not math.isfinite(number):
                    raise ValueError
            except ValueError:
                st.warning("Please enter a finite number.")
            else:
                if number == expected:
                    st.success("Correct! " + explanation)
                else:
                    st.warning("Not correct yet. " + explanation)
