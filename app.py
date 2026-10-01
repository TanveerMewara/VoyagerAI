import streamlit as st
import time
import re
from io import BytesIO

from agents.supervisor_agent import supervisor_agent
from tools.pdf_generator import generate_pdf
from tools.map import create_map

from utils.gemini import ask_followup
from utils.workflow import create_workflow
from utils.budget_chart import create_budget_chart

from streamlit_folium import st_folium

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Voyager AI",
    page_icon="✈️",
    layout="wide"
)

# ==========================================================
# SESSION STATE
# ==========================================================

if "travel_plan" not in st.session_state:
    st.session_state.travel_plan = ""

if "trip_details" not in st.session_state:
    st.session_state.trip_details = {}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "execution_time" not in st.session_state:
    st.session_state.execution_time = 0

# ==========================================================
# LOAD CSS
# ==========================================================

with open("assets/style.css") as f:

    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

# ==========================================================
# HEADER
# ==========================================================

st.markdown(
    """
    <div class='main-title'>
        🌍 Voyager AI
    </div>

    <div class='sub-title'>
        Autonomous Multi-Agent Travel Intelligence Platform
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# ==========================================================
# MAIN LAYOUT
# ==========================================================

left, right = st.columns([2,1])

# ==========================================================
# LEFT PANEL
# ==========================================================

with left:

    st.subheader("📝 Trip Details")

    destination = st.text_input(
        "📍 Destination",
        placeholder="e.g. Japan"
    )

    days = st.number_input(
        "📅 Number of Days",
        min_value=1,
        max_value=30,
        value=5
    )

    budget = st.text_input(
        "💰 Budget",
        placeholder="e.g. ₹80,000"
    )

    travelers = st.selectbox(
        "👨‍👩‍👧 Travelers",
        [
            "Solo",
            "Couple",
            "Family",
            "Friends"
        ]
    )

    departure = st.text_input(
        "✈️ Departure City",
        placeholder="e.g. Jaipur"
    )

    interests = st.text_area(
        "🎯 Interests",
        placeholder="Adventure, Beaches, Food, Nature..."
    )

# ==========================================================
# RIGHT PANEL
# ==========================================================

with right:

    st.subheader("🤖 AI Agent Dashboard")

    planner_status = st.empty()

    budget_status = st.empty()

    hotel_status = st.empty()

    weather_status = st.empty()

st.divider()

generate = st.button(
    "🚀 Generate Intelligent Travel Plan",
    width="stretch"
)

st.subheader("🖥 Supervisor Console")

console = st.empty()

st.divider()

# ==========================================================
# GENERATE PLAN
# ==========================================================

if "generation_error" in st.session_state:
    st.error(st.session_state.pop("generation_error"))

if generate:

    start_time = time.perf_counter()

    if destination.strip() == "":

        st.warning("Please enter a destination.")

        st.stop()

    progress = st.progress(0)

    status = st.empty()

    # status.info("🧠 Supervisor Agent received your request...")

    console.code(
    """
    [INFO] Supervisor Agent received travel request...

    [INFO] Assigning itinerary generation to Planner Agent...
    """,
    language="text"
    )

    progress.progress(10)


    planner_status.info("🟡 Planner Agent Working...")

    status.info("📅 Building itinerary...")

    progress.progress(30)


    budget_status.info("🟡 Budget Agent Working...")

    status.info("💰 Calculating budget...")

    progress.progress(50)


    hotel_status.info("🟡 Hotel Agent Working...")

    status.info("🏨 Finding hotels...")

    progress.progress(70)


    weather_status.info("🟡 Weather Tool Working...")

    status.info("🌤 Fetching weather...")

    progress.progress(90)

    preview = st.empty()

    try:

        response = supervisor_agent(
            destination,
            days,
            budget,
            travelers,
            interests,
            departure,
            on_chunk=preview.markdown
        )

    except Exception as e:

        if st.session_state.travel_plan:
            st.session_state.generation_error = (
                f"The new request failed. Your previous plan is still available. {e}"
            )
            st.rerun()

        st.error(f"❌ {e}")

        st.stop()

    preview.empty()
    execution_time = round(time.perf_counter() - start_time, 2)

    st.session_state.execution_time = execution_time

    st.session_state.travel_plan = response
    st.session_state.chat_history = []
    st.session_state.pop("pdf_report", None)

    st.session_state.trip_details = {

        "destination": destination,
        "days": days,
        "budget": budget,
        "travelers": travelers,
        "departure": departure,
        "interests": interests

    }

    planner_status.success("✅ Planner Completed")

    budget_status.success("✅ Budget Completed")

    hotel_status.success("✅ Hotel Completed")

    weather_status.success("✅ Weather Retrieved")

    progress.progress(100)

    status.success("📄 Travel Report Generated Successfully")

# ==========================================================
# DISPLAY SAVED REPORT
# ==========================================================

if st.session_state.travel_plan:

    response = st.session_state.travel_plan

    trip = st.session_state.trip_details

    destination = trip["destination"]
    days = trip["days"]
    budget = trip["budget"]
    travelers = trip["travelers"]
    departure = trip["departure"]
    interests = trip["interests"]

    # st.balloons()

    st.success(
        "🎉 Voyager AI successfully generated your personalized travel plan!"
    )

    st.info(
        "This travel itinerary was created using a Supervisor Agent coordinating multiple specialized AI agents."
    )

    st.divider()

    # ==========================================================
    # BUDGET ANALYTICS
    # ==========================================================

    st.subheader("🌍 AI Generated Travel Report")

    sections = re.split(r"(?m)(?=^#\s)", response)

    for section in sections:

        section = re.sub(r"(?m)^---[ \t]*$", "", section).strip()

        if section:

            title = section.split("\n")[0]

            with st.expander(
                title,
                expanded=True
            ):

                st.markdown(section)

    st.divider()

    st.subheader("📊 Budget Analytics")

    try:

        budget_chart = create_budget_chart(budget)

        st.plotly_chart(
            budget_chart,
            width="stretch"
        )

    except Exception as e:

        st.warning(
            f"Unable to generate budget chart.\n\n{e}"
        )

    st.divider()

    # ==========================================================
    # MULTI AGENT WORKFLOW
    # ==========================================================

    st.subheader("🧠 Multi-Agent Workflow")

    try:

        workflow = create_workflow()

        st.graphviz_chart(
            workflow,
            use_container_width=True
        )

    except Exception as e:

        st.warning(
            f"Workflow could not be displayed.\n\n{e}"
        )

    st.divider()

    # ==========================================================
    # TRIP SUMMARY
    # ==========================================================

    st.subheader("⚡ AI Execution Summary")

    m1, m2, m3, m4, m5 = st.columns(5)

    m1.metric(
        "🤖 Agents",
        "5"
    )

    m2.metric(
        "✅ Tasks",
        "5"
    )

    m3.metric(
        "⚡ Time",
        f"{st.session_state.execution_time} sec"
    )

    m4.metric(
        "🧠 Model",
        "Gemini 2.5 Flash"
    )

    m5.metric(
        "📄 Status",
        "Completed"
    )

    st.divider()

    st.subheader("📊 Trip Summary")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "📍 Destination",
        destination
    )

    c2.metric(
        "📅 Duration",
        f"{days} Days"
    )

    c3.metric(
        "👨‍👩‍👧 Travelers",
        travelers
    )

    c4.metric(
        "💰 Budget",
        budget
    )

    st.divider()

    # ==========================================================
    # DESTINATION MAP
    # ==========================================================

    st.subheader("🗺️ Destination Map")

    try:

        travel_map = create_map(destination)

        st_folium(
            travel_map,
            width=900,
            height=450,
            returned_objects=[]
        )

    except Exception as e:

        st.warning(
            f"Unable to load destination map.\n\n{e}"
        )

    st.divider()

    # ==========================================================
    # AI GENERATED REPORT
    # ==========================================================

    # ==========================================================
    # DOWNLOAD REPORT
    # ==========================================================

    st.subheader("📄 Download Travel Report")

    try:

        if "pdf_report" not in st.session_state:
            pdf_buffer = BytesIO()
            generate_pdf(response, filename=pdf_buffer)
            st.session_state.pdf_report = pdf_buffer.getvalue()

        st.download_button(
                label="📥 Download Complete Travel Plan",
                data=st.session_state.pdf_report,
                file_name="VoyagerAI_TravelPlan.pdf",
                mime="application/pdf",
                width="stretch",
                on_click="ignore"
            )

    except Exception as e:

        st.warning(
            f"Unable to generate PDF.\n\n{e}"
        )

    st.divider()

    # ==========================================================
    # AI CHAT
    # ==========================================================

    st.divider()

    with st.expander("🧠 Why did Voyager AI recommend this plan?"):

        st.markdown("""
    ### Recommendation Factors

    ✅ Destination analyzed

    ✅ Budget considered

    ✅ Number of travel days optimized

    ✅ Traveler type considered

    ✅ Interests matched

    ✅ Hotels selected

    ✅ Weather checked

    ✅ Activities balanced

    ✅ Final itinerary generated by Supervisor Agent
    """)

    st.subheader("💬 Continue Chat with Voyager AI")

    st.caption(
        "Ask follow-up questions without generating a new travel plan."
    )

    user_question = st.chat_input(
        "Ask about hotels, budget, itinerary, transport..."
    )

    if user_question:

        chat_preview = st.empty()
        st.session_state.chat_history.append(
            (
                "user",
                user_question
            )
        )

        with st.spinner("🤖 Voyager AI is thinking..."):

            try:

                answer = ask_followup(
                    st.session_state.travel_plan,
                    user_question,
                    on_chunk=chat_preview.markdown
                )

            except Exception as e:

                answer = f"❌ {e}"

        st.session_state.chat_history.append(
            (
                "assistant",
                answer
            )
        )
        chat_preview.empty()

    for role, message in st.session_state.chat_history:

        with st.chat_message(role):

            st.markdown(message)

    st.divider()

    # ==========================================================
    # END OF MAIN CONTENT
    # ==========================================================

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.title("✈️ Voyager AI")

    st.markdown("---")

    st.subheader("🤖 AI Agents")

    st.success("🧠 Supervisor Agent")

    st.success("📅 Planner Agent")

    st.success("💰 Budget Agent")

    st.success("🏨 Hotel Agent")

    st.success("🌤 Weather Tool")

    st.markdown("---")

    st.subheader("🚀 Tech Stack")

    st.write("🐍 Python")

    st.write("🤖 Google Gemini")

    st.write("🖥 Streamlit")

    st.write("🗺 Folium")

    st.write("📊 Plotly")

    st.write("📄 ReportLab")

    st.write("🔀 LangGraph")

    st.markdown("---")

    st.subheader("📈 Project Statistics")

    if st.session_state.travel_plan:

        trip = st.session_state.trip_details

        st.metric(
            "Destination",
            trip["destination"]
        )

        st.metric(
            "Duration",
            f"{trip['days']} Days"
        )

        st.metric(
            "Travelers",
            trip["travelers"]
        )

    else:

        st.info(
            "Generate a travel plan to view trip statistics."
        )

    st.markdown("---")

    st.subheader("💡 About Voyager AI")

    st.write(
        """
Voyager AI is a Supervisor-based Multi-Agent Travel Planning System.

The Supervisor Agent coordinates multiple specialized AI agents:

• Planner Agent

• Budget Agent

• Hotel Agent

• Weather Tool

to generate a complete personalized travel itinerary.
"""
    )

    st.markdown("---")

    st.success("✅ AI Agents Ready")

    st.caption("Version 2.0")

# ==========================================================
# FOOTER
# ==========================================================

st.divider()

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown("### 🌍 Voyager AI")

    st.write(
        "An Autonomous Multi-Agent Travel Intelligence Platform."
    )

with col2:

    st.markdown("### 🤖 AI Features")

    st.write("• Personalized Itinerary")

    st.write("• Budget Planning")

    st.write("• Hotel Suggestions")

    st.write("• Weather Information")

    st.write("• Interactive Travel Chat")

with col3:

    st.markdown("### 🚀 Built Using")

    st.write("Python")

    st.write("Google Gemini AI")

    st.write("Streamlit")

    st.write("LangGraph")

    st.write("Folium")

    st.write("Plotly")

st.divider()

st.markdown(
    """
<div style="text-align:center; padding:15px;">

### ❤️ Voyager AI

Built as a Multi-Agent AI project demonstrating autonomous task planning,
agent orchestration, conversational AI, mapping, visualization and PDF reporting.

**Designed & Developed by Tanveer Mewara**

</div>
""",
    unsafe_allow_html=True
)
