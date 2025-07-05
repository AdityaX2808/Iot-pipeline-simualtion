import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------- Page Setup --------------------
st.set_page_config(
    page_title="Vehicle Health Monitoring & Predictive Maintenance",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- Load Data --------------------
@st.cache_data  
def load_data():
    df = pd.read_parquet("./datasource/v2_cleaned.parquet")
    df["timeStamp"] = pd.to_datetime(df["timeStamp"])
    df["deviceID"] = df["deviceID"].astype(str)
    df["dtc"] = df["dtc"].astype(str)
    return df

df = load_data()
device_ids = sorted(df["deviceID"].unique())

# -------------------- Sidebar Filters --------------------
st.sidebar.title(" Filter Options")
select_all = st.sidebar.checkbox("Select All Devices", value=True)
selected_devices = device_ids if select_all else st.sidebar.multiselect("Choose Device(s)", device_ids)

# Filter Data
df_filtered = df[df["deviceID"].isin(selected_devices)]

if df_filtered.empty:
    st.warning("⚠️ No data available for the selected device(s).")
    st.stop()

# -------------------- Header --------------------
st.markdown("# **Vehicle Health Monitoring & Predictive Maintenance**")

# -------------------- KPIs --------------------
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric(" **Avg Battery (V)**", f"{df_filtered['battery'].mean():.2f}")
kpi2.metric(" **Avg RPM**", f"{df_filtered['rpm'].mean():.0f}")
kpi3.metric(" **Engine Load (%)**", f"{df_filtered['eLoad'].mean():.1f}%")
kpi4.metric(" **Coolant Temp (°C)**", f"{df_filtered['cTemp'].mean():.1f}")
kpi5.metric(" **Active DTCs**", f"{df_filtered[df_filtered['dtc'] != '0'].shape[0]}")

# -------------------- Alert Summary --------------------
alert_conditions = {
    "High RPM (>3000)": df_filtered["rpm"] > 3000,
    "Overheating (>90°C)": df_filtered["cTemp"] > 90,
    "Low Battery (<5V)": df_filtered["battery"] < 5,
    "High Load (>70%)": df_filtered["eLoad"] > 70,
    "DTC Triggered": df_filtered["dtc"] != "0"
}

alert_counts = {k: v.sum() for k, v in alert_conditions.items() if v.sum() > 0}

if alert_counts:
    with st.container():
        st.markdown("""
            <div style='background-color:#8B0000;padding:15px;border-radius:10px'>
                <h3 style='color:white'> Alert Summary</h3>
                <ul style='color:white'>
        """, unsafe_allow_html=True)
        for k, v in alert_counts.items():
            st.markdown(f"<li> {k}: {v} events</li>", unsafe_allow_html=True)
        st.markdown("""
                </ul>
            </div>
        """, unsafe_allow_html=True)
else:
    st.success(" No critical alerts for the selected devices.")

# -------------------- Metric Over Time --------------------
st.markdown("## Metric Over Time")
metric = st.selectbox("Select Metric", ["rpm", "battery", "eLoad", "cTemp", "speed"])
fig_line = px.line(df_filtered, x="timeStamp", y=metric, color="deviceID", height=350)
fig_line.update_layout(margin=dict(t=30))
st.plotly_chart(fig_line, use_container_width=True)

# -------------------- Bar Chart --------------------
st.markdown("## Average Metrics per Device")
avg_df = df_filtered.groupby("deviceID")[["rpm", "battery", "eLoad", "cTemp"]].mean().reset_index()
fig_bar = px.bar(avg_df.melt(id_vars="deviceID"), x="deviceID", y="value", color="variable",
                 barmode="group", height=350)
st.plotly_chart(fig_bar, use_container_width=True)

# -------------------- Scatter Plot --------------------
st.markdown("##  RPM vs Engine Load")
fig_scatter = px.scatter(df_filtered, x="rpm", y="eLoad", color="deviceID", hover_data=["timeStamp"], height=350)
st.plotly_chart(fig_scatter, use_container_width=True)

# -------------------- Aggregated Table --------------------
st.markdown("## Device Overview Table")
overview = df_filtered.groupby("deviceID")[["rpm", "battery", "eLoad", "cTemp"]]
overview = overview.agg(['mean', 'max', 'min']).round(2)
st.dataframe(overview, use_container_width=True)

# -------------------- Maintenance Recommendations --------------------
st.markdown("## Maintenance Recommendations")
recommendations = []
for device in df_filtered["deviceID"].unique():
    df_dev = df_filtered[df_filtered["deviceID"] == device]
    issues = []
    if (df_dev["battery"] < 11).any(): issues.append("Battery voltage low")
    if (df_dev["cTemp"] > 110).any(): issues.append("Coolant overheating")
    if (df_dev["rpm"] > 5000).any(): issues.append("High RPM - risk of engine wear")
    if (df_dev["eLoad"] > 90).any(): issues.append("Engine load high")
    if (df_dev["dtc"] != "0").any(): issues.append("DTC codes present")
    if issues:
        summary = f" **Vehicle {device}**: {', '.join(issues)}"
        recommendations.append(summary)

if recommendations:
    for item in recommendations:
        st.warning(item)
else:
    st.success("✅ All selected vehicles are operating within healthy thresholds.")

# -------------------- Hide Footer --------------------
st.markdown("""
    <style>
        #MainMenu, footer {visibility: hidden;}
        .block-container {padding-top: 1rem;}
    </style>
""", unsafe_allow_html=True)
