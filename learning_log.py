import json
import uuid
from datetime import datetime, timezone
import streamlit as st


def prepare_log():
    if "demo_log_events" not in st.session_state:
        st.session_state.demo_log_events = []
        st.session_state.demo_log_id = str(uuid.uuid4())


def record_event(event_type, **details):
    prepare_log()
    st.session_state.demo_log_events.append({
        "event_number": len(st.session_state.demo_log_events) + 1,
        "session_id": st.session_state.demo_log_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "challenge": st.session_state.get("child_task", 0) + 1,
        "event_type": event_type,
        **details,
    })


def show_log():
    prepare_log()
    with st.expander("Developer tools: interaction log"):
        st.caption(
            "Records stay in this app session until you download them. "
            "Refreshing or closing the session can lose unsaved records."
        )
        events = st.session_state.demo_log_events
        st.write(f"Recorded events: {len(events)}")

        if events:
            st.dataframe(events, use_container_width=True)
            st.download_button(
                "Download interaction log",
                data=json.dumps(events, indent=2),
                file_name=f"demo_{st.session_state.demo_log_id}.json",
                mime="application/json",
            )

        if st.button("Clear log and restart demo"):
            for key in list(st.session_state):
                if key.startswith(("child_", "demo_log_")):
                    del st.session_state[key]
            st.rerun()
