
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="SAMA Sentinel", page_icon="🏦", layout="wide")

# --- Load data ---
df = pd.read_csv("sama_merged.csv", parse_dates=["date"])
df = df.sort_values("date")

# --- Header ---
st.title("🏦 SAMA Sentinel")
st.markdown("**Saudi Central Bank Policy Monitor** | Hawkish/Dovish Analysis Dashboard")
st.divider()

# --- Row 1: Key Metrics ---
col1, col2, col3, col4 = st.columns(4)
latest = df.iloc[-1]
col1.metric("Latest Score",     f"{latest.hawkish_score}/10")
col2.metric("Stance",           latest.stance)
col3.metric("Inflation",        f"{latest.inflation:.1f}%")
col4.metric("SIBOR (3M)",       f"{latest.sibor:.2f}%")

st.divider()

# --- Row 2: Policy Heat Index Chart ---
st.subheader("📈 Policy Heat Index Over Time")

fig = go.Figure()
colors = ["red" if s == "Hawkish" else "blue" if s == "Dovish" else "gray"
          for s in df["stance"]]

fig.add_trace(go.Scatter(
    x=df["date"], y=df["hawkish_score"],
    mode="lines+markers",
    line=dict(color="orange", width=2),
    marker=dict(color=colors, size=12, line=dict(width=2, color="white")),
    hovertemplate="<b>%{x}</b><br>Score: %{y}/10<extra></extra>"
))

fig.add_hline(y=6, line_dash="dash", line_color="red",   annotation_text="Hawkish threshold")
fig.add_hline(y=4, line_dash="dash", line_color="blue",  annotation_text="Dovish threshold")
fig.update_layout(
    yaxis=dict(range=[0,10], title="Hawkish Score (1=Dovish, 10=Hawkish)"),
    xaxis_title="Date",
    height=400,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Row 3: Document Explorer + Economic Indicators side by side ---
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("🔍 Document Explorer")
    selected_date = st.selectbox(
        "Select a report date:",
        options=df["date"].dt.strftime("%Y-%m-%d").tolist()
    )
    row = df[df["date"].dt.strftime("%Y-%m-%d") == selected_date].iloc[0]

    stance_color = "🔴" if row.stance == "Hawkish" else "🔵" if row.stance == "Dovish" else "⚪"
    st.markdown(f"**File:** {row.filename}")
    st.markdown(f"**Stance:** {stance_color} {row.stance}")
    st.markdown(f"**Score:** {row.hawkish_score}/10")
    st.markdown("**Key Phrases Detected:**")
    for phrase in str(row.key_phrases).split(" | "):
        st.markdown(f"- {phrase}")

with col_right:
    st.subheader("📊 Economic Indicators")
    econ_df = df[["date","inflation","reserves","sibor"]].copy()
    econ_df["date"] = econ_df["date"].dt.strftime("%Y-%m-%d")
    econ_df.columns = ["Date", "Inflation (%)", "Reserves (USD bn)", "SIBOR 3M (%)"]
    st.dataframe(econ_df, use_container_width=True, hide_index=True)

st.divider()

# --- Row 4: What-If Oil Price Slider ---
st.subheader("🎚️ What-If Scenario: Oil Price Shock")
oil_change = st.slider(
    "If oil price changes by (%):",
    min_value=-50, max_value=50, value=0, step=5
)

if oil_change != 0:
    direction = "rise" if oil_change > 0 else "fall"
    if oil_change > 20:
        response = "📈 Oil windfall likely → SAMA may accumulate reserves. Inflation risk rises. Policy could lean **Hawkish**."
    elif oil_change > 0:
        response = "📊 Moderate oil gain → Stable reserves. Neutral policy stance expected."
    elif oil_change > -20:
        response = "📉 Mild oil decline → Some reserve drawdown. SAMA likely holds rates steady."
    else:
        response = "⚠️ Sharp oil drop → Significant reserve pressure. Fiscal stimulus likely. Policy may turn **Dovish**."
    st.info(f"**Oil price {direction} of {abs(oil_change)}%** → {response}")
else:
    st.info("Move the slider to simulate an oil price scenario.")

st.divider()
st.caption("SAMA Sentinel | Built with Python, Streamlit & Plotly | Data: SAMA, World Bank")
