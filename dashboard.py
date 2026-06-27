import streamlit as st
import pandas as pd
import plotly.express as px
import httpx
import time
import os

st.set_page_config(page_title="Hotel Intelligence | AI Dashboard", page_icon="🏛️", layout="wide")

st.markdown("""
    <style>
    .main { background: #0b0e14; color: #e1e1e1; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background: #11151c; border-right: 1px solid #1f2937; }
    .stMetric {
        background: rgba(31, 41, 55, 0.4);
        padding: 20px; border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(8px);
    }
    .critical-card {
        background: rgba(239, 68, 68, 0.1);
        padding: 18px; border-radius: 10px;
        border-left: 5px solid #ef4444;
        margin-bottom: 12px;
        transition: transform 0.2s;
    }
    .critical-card:hover { transform: translateX(5px); }
    h1, h2, h3 { color: #f9fafb; font-weight: 800; }
    .stButton>button {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        color: white; border: none; padding: 10px 24px; border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

API_URL = os.getenv("API_URL", "http://localhost:8000")
API_V1 = f"{API_URL}/api/v1"

if "access_token" not in st.session_state:
    st.session_state.access_token = None


def auth_headers():
    if st.session_state.access_token:
        return {"Authorization": f"Bearer {st.session_state.access_token}"}
    return {}


def get_api_data(endpoint):
    try:
        with httpx.Client(timeout=10) as client:
            response = client.get(f"{API_V1}/{endpoint}", headers=auth_headers())
            if response.status_code != 200:
                return None
            return response.json().get("data")
    except Exception:
        return None


st.sidebar.markdown("### Account")
login_email = st.sidebar.text_input("Email", value="demo@hotel.com")
login_password = st.sidebar.text_input("Password", type="password", value="demopass123")

if st.sidebar.button("Login"):
    with httpx.Client(timeout=10) as client:
        response = client.post(
            f"{API_V1}/auth/login",
            data={"username": login_email, "password": login_password},
        )
    if response.status_code == 200:
        st.session_state.access_token = response.json()["data"]["access_token"]
        st.sidebar.success("Signed in")
    else:
        st.sidebar.error("Login failed. Register a user or run seed_data.py for demo credentials.")

if st.session_state.access_token and st.sidebar.button("Logout"):
    st.session_state.access_token = None
    st.rerun()

st.markdown("# 🏛️ Hotel Intelligence Platform")
st.markdown(
    "<p style='color: #9ca3af; font-size: 1.2em;'>Live Aspect-Based Sentiment Analysis (ABSA) Engine</p>",
    unsafe_allow_html=True,
)

if not st.session_state.access_token:
    st.warning("Sign in from the sidebar to access your hotel analytics.")
    st.stop()

st.sidebar.markdown("### 🗺️ Navigation")
page = st.sidebar.selectbox("Jump to", ["Market Intelligence", "Bulk Processing", "Live Logs"])

if page == "Market Intelligence":
    stats = get_api_data("analytics/stats")

    if stats:
        m1, m2, m3 = st.columns(3)
        m1.metric("Processed Intelligence", f"{stats['total_reviews']:,}", "Reviews")

        avg_score = (
            sum(a["avg_score"] for a in stats["aspect_breakdown"]) / len(stats["aspect_breakdown"])
            if stats["aspect_breakdown"]
            else 0
        )
        m2.metric("Guest Sentiment (Vibe)", f"{avg_score * 100:.1f}%", f"{(avg_score - 0.5) * 10:+,.1f}% vs Goal")
        m3.metric("Detected Anomalies", f"{len(stats['critical_issues'])} Items", "Issues Found")

        st.divider()

        col_left, col_right = st.columns([1.5, 1])

        with col_left:
            st.subheader("📊 Aspect 'Vibe' Heatmap")
            if stats["aspect_breakdown"]:
                df_aspects = pd.DataFrame(stats["aspect_breakdown"])
                fig = px.bar(
                    df_aspects,
                    x="aspect",
                    y="avg_score",
                    color="avg_score",
                    title="Intelligence Intensity by Segment",
                    color_continuous_scale="Viridis",
                    range_color=[0, 1],
                    template="plotly_dark",
                )
                fig.update_layout(
                    margin=dict(l=20, r=20, t=40, b=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data yet. Upload reviews to see analytics.")

        with col_right:
            st.subheader("🚨 Dynamic Intelligence Alerts")
            for issue in stats["critical_issues"]:
                st.markdown(
                    f"""
                    <div class="critical-card">
                        <span style='font-size: 0.8em; color: #9ca3af; text-transform: uppercase;'>Anomaly Type: High Impact</span><br/>
                        <strong style='font-size: 1.2em; color: #f9fafb;'>{issue['issue']}</strong><br/>
                        <small style='color: #ef4444;'>Impact: {issue['impact']} | Profile: {issue['frequency']}</small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.error("Could not load analytics. Check API connection and authentication.")

elif page == "Bulk Processing":
    st.subheader("📤 CSV Review Upload")
    st.markdown("Upload a Kaggle-compatible CSV (`Hotel_Name`, `Full_Review` or `Negative_Review`/`Positive_Review`).")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file and st.button("🚀 Start Analysis"):
        file_bytes = uploaded_file.getvalue()

        with httpx.Client(timeout=60) as client:
            response = client.post(
                f"{API_V1}/jobs/csv-upload",
                headers=auth_headers(),
                files={"file": (uploaded_file.name, file_bytes, "text/csv")},
            )

            if response.status_code != 200:
                st.error(f"Upload failed: {response.text}")
            else:
                task_id = response.json()["data"]["task_id"]
                progress_bar = st.progress(0.0)
                status_text = st.empty()

                while True:
                    status_response = client.get(
                        f"{API_V1}/jobs/{task_id}",
                        headers=auth_headers(),
                    )
                    if status_response.status_code != 200:
                        st.error("Could not fetch job status.")
                        break

                    status = status_response.json()["data"]
                    progress_bar.progress(status["progress"])
                    status_text.write(
                        f"Status: **{status['status']}** — "
                        f"{status['processed_reviews']}/{status['total_reviews']} reviews processed"
                    )

                    if status["status"] in {"COMPLETED", "FAILED"}:
                        if status["status"] == "COMPLETED":
                            st.success("Bulk analysis complete.")
                            st.balloons()
                        else:
                            st.error(status.get("error_message", "Bulk analysis failed."))
                        break

                    time.sleep(1)

elif page == "Live Logs":
    st.subheader("📡 Real-Time Intelligence Feed")
    st.markdown("<small style='color: #6b7280;'>Last 10 Analyzed Reviews</small>", unsafe_allow_html=True)

    feed = get_api_data("reviews/latest")
    if feed:
        for entry in feed:
            with st.container():
                st.markdown(f"#### 🏨 {entry['hotel'] or 'Hotel'}")
                st.write(f'"{entry["text"]}"')

                tag_html = ""
                for analysis in entry["analysis"]:
                    color = "#10b981" if analysis["sentiment"] == "POSITIVE" else "#ef4444"
                    tag_html += f"""
                        <span style='background: {color}22; color: {color}; border: 1px solid {color}; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; margin-right: 5px;'>
                            {analysis['aspect']}: {analysis['sentiment']}
                        </span>
                    """
                st.markdown(tag_html, unsafe_allow_html=True)
                st.divider()
    else:
        st.info("No reviews yet. Upload a CSV to start analysis.")

st.sidebar.markdown("---")
st.sidebar.caption("🤖 Model: DistilBERT SST-2")
st.sidebar.caption("⚙️ Backend: FastAPI + PostgreSQL + JWT")
st.sidebar.caption("📦 Background jobs: FastAPI BackgroundTasks")
