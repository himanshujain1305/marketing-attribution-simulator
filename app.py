import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Marketing Attribution Simulator",
    page_icon="📊",
    layout="wide"
)

SAMPLE_PATH = Path("sample_data/sample_customer_journeys.csv")

st.title("📊 Marketing Attribution Simulator")

st.markdown(
    """
    Compare how marketing channel performance changes under different attribution models.
    
    This tool helps answer:
    - Which channels get credit under first-touch vs. last-touch attribution?
    - Which channels are undervalued by simple attribution models?
    - How does ROI change when revenue credit is distributed differently?
    """
)

@st.cache_data
def load_csv(file):
    return pd.read_csv(file)

def clean_data(df):
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df["touch_date"] = pd.to_datetime(df["touch_date"])
    df["converted"] = df["converted"].astype(int)
    df["revenue"] = df["revenue"].astype(float)
    df["cost"] = df["cost"].astype(float)
    return df

def check_required_columns(df):
    required = [
        "customer_id",
        "touch_number",
        "touch_date",
        "channel",
        "campaign",
        "converted",
        "revenue",
        "cost",
    ]
    return [col for col in required if col not in df.columns]

def get_conversion_journeys(df):
    converted_customers = df.groupby("customer_id")["converted"].max()
    converted_ids = converted_customers[converted_customers == 1].index
    return df[df["customer_id"].isin(converted_ids)].copy()

def calculate_first_touch(df):
    converted_df = get_conversion_journeys(df)
    first_touches = (
        converted_df.sort_values(["customer_id", "touch_number"])
        .groupby("customer_id")
        .first()
        .reset_index()
    )

    final_revenue = (
        converted_df.groupby("customer_id")["revenue"]
        .max()
        .reset_index()
        .rename(columns={"revenue": "attributed_revenue"})
    )

    result = first_touches[["customer_id", "channel"]].merge(final_revenue, on="customer_id")
    return result

def calculate_last_touch(df):
    converted_df = get_conversion_journeys(df)
    last_touches = (
        converted_df.sort_values(["customer_id", "touch_number"])
        .groupby("customer_id")
        .last()
        .reset_index()
    )

    result = last_touches[["customer_id", "channel", "revenue"]].rename(
        columns={"revenue": "attributed_revenue"}
    )
    return result

def calculate_linear(df):
    converted_df = get_conversion_journeys(df)
    journey_counts = (
        converted_df.groupby("customer_id")["touch_number"]
        .count()
        .reset_index()
        .rename(columns={"touch_number": "touch_count"})
    )

    revenue = (
        converted_df.groupby("customer_id")["revenue"]
        .max()
        .reset_index()
        .rename(columns={"revenue": "total_revenue"})
    )

    result = converted_df.merge(journey_counts, on="customer_id").merge(revenue, on="customer_id")
    result["attributed_revenue"] = result["total_revenue"] / result["touch_count"]
    return result[["customer_id", "channel", "attributed_revenue"]]

def calculate_time_decay(df, decay_rate=0.6):
    converted_df = get_conversion_journeys(df)

    rows = []

    for customer_id, group in converted_df.groupby("customer_id"):
        group = group.sort_values("touch_number").copy()
        total_revenue = group["revenue"].max()

        if total_revenue <= 0:
            continue

        max_touch = group["touch_number"].max()
        group["distance_from_conversion"] = max_touch - group["touch_number"]
        group["weight"] = decay_rate ** group["distance_from_conversion"]
        group["weight_share"] = group["weight"] / group["weight"].sum()
        group["attributed_revenue"] = group["weight_share"] * total_revenue

        rows.append(group[["customer_id", "channel", "attributed_revenue"]])

    if not rows:
        return pd.DataFrame(columns=["customer_id", "channel", "attributed_revenue"])

    return pd.concat(rows, ignore_index=True)

def summarize_attribution(attribution_df, costs_df, model_name):
    revenue_summary = (
        attribution_df.groupby("channel")["attributed_revenue"]
        .sum()
        .reset_index()
    )

    conversions_summary = (
        attribution_df.groupby("channel")["customer_id"]
        .nunique()
        .reset_index()
        .rename(columns={"customer_id": "attributed_conversions"})
    )

    cost_summary = (
        costs_df.groupby("channel")["cost"]
        .sum()
        .reset_index()
    )

    summary = revenue_summary.merge(conversions_summary, on="channel", how="left")
    summary = summary.merge(cost_summary, on="channel", how="left")
    summary["model"] = model_name
    summary["roi"] = np.where(
        summary["cost"] > 0,
        (summary["attributed_revenue"] - summary["cost"]) / summary["cost"],
        0
    )

    return summary

def build_model_comparison(df):
    first = summarize_attribution(calculate_first_touch(df), df, "First-touch")
    last = summarize_attribution(calculate_last_touch(df), df, "Last-touch")
    linear = summarize_attribution(calculate_linear(df), df, "Linear")
    time_decay = summarize_attribution(calculate_time_decay(df), df, "Time-decay")

    return pd.concat([first, last, linear, time_decay], ignore_index=True)

def generate_insights(model_df):
    insights = []

    last_touch = model_df[model_df["model"] == "Last-touch"]
    first_touch = model_df[model_df["model"] == "First-touch"]
    linear = model_df[model_df["model"] == "Linear"]

    if not last_touch.empty:
        top_last = last_touch.sort_values("attributed_revenue", ascending=False).iloc[0]
        insights.append(
            f"Under last-touch attribution, **{top_last['channel']}** receives the most revenue credit."
        )

    if not first_touch.empty:
        top_first = first_touch.sort_values("attributed_revenue", ascending=False).iloc[0]
        insights.append(
            f"Under first-touch attribution, **{top_first['channel']}** looks strongest for initial demand creation."
        )

    if not linear.empty:
        top_linear = linear.sort_values("roi", ascending=False).iloc[0]
        insights.append(
            f"Under linear attribution, **{top_linear['channel']}** has the strongest ROI because credit is shared across the journey."
        )

    insights.append(
        "Do not make budget decisions from one attribution model alone. Compare models to understand which channels create demand, nurture demand, and close conversions."
    )

    return insights

st.sidebar.header("Data input")

use_sample = st.sidebar.checkbox("Use sample customer journey dataset", value=True)
uploaded_file = st.sidebar.file_uploader("Or upload your own CSV", type=["csv"])

if uploaded_file is not None:
    df = load_csv(uploaded_file)
elif use_sample and SAMPLE_PATH.exists():
    df = load_csv(SAMPLE_PATH)
else:
    st.warning("Upload a CSV or add sample_data/sample_customer_journeys.csv")
    st.stop()

df = clean_data(df)

missing = check_required_columns(df)
if missing:
    st.error(f"Missing required columns: {missing}")
    st.stop()

st.subheader("Executive summary")

total_customers = df["customer_id"].nunique()
converted_customers = df.groupby("customer_id")["converted"].max().sum()
conversion_rate = converted_customers / total_customers if total_customers else 0
total_revenue = df["revenue"].sum()
total_cost = df["cost"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Customers", f"{total_customers:,}")
col2.metric("Converted customers", f"{converted_customers:,}")
col3.metric("Conversion rate", f"{conversion_rate:.1%}")
col4.metric("Total revenue", f"${total_revenue:,.0f}")

st.caption(f"Total marketing touch cost in dataset: ${total_cost:,.0f}")

st.divider()

model_df = build_model_comparison(df)

tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Model comparison", "📈 Channel ROI", "🧠 Insights", "📄 Data"]
)

with tab1:
    st.subheader("Revenue credited by attribution model")

    fig = px.bar(
        model_df,
        x="channel",
        y="attributed_revenue",
        color="model",
        barmode="group",
        title="Attributed revenue by channel and model",
        text_auto=".2s"
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Attributed revenue",
        xaxis_tickangle=-25,
        margin=dict(l=20, r=20, t=60, b=120),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Attribution summary table")
    display_df = model_df.copy()
    display_df["attributed_revenue"] = display_df["attributed_revenue"].round(2)
    display_df["roi"] = display_df["roi"].round(2)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("ROI by channel and attribution model")

    fig = px.bar(
        model_df,
        x="channel",
        y="roi",
        color="model",
        barmode="group",
        title="ROI changes depending on attribution model",
        text_auto=".2f"
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="ROI",
        xaxis_tickangle=-25,
        margin=dict(l=20, r=20, t=60, b=120),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        """
        **How to read this:**  
        A channel may look weak under last-touch attribution but stronger under first-touch or linear attribution.
        That usually means the channel may be helping create or nurture demand even if it is not closing the final conversion.
        """
    )

with tab3:
    st.subheader("Marketing interpretation")

    for insight in generate_insights(model_df):
        st.markdown(f"- {insight}")

    st.markdown("### Recommended next move")
    st.info(
        "Use attribution models as directional lenses, not absolute truth. "
        "Before cutting or scaling a channel, check whether it plays an awareness, nurture, or closing role in the journey."
    )

    action_plan = """
# Marketing Attribution Action Plan

## What this analysis shows
Different attribution models assign revenue credit differently. A channel can look strong or weak depending on whether you measure first-touch, last-touch, linear, or time-decay attribution.

## How to use this
- Use first-touch attribution to understand demand creation.
- Use last-touch attribution to understand conversion capture.
- Use linear attribution to understand full-journey contribution.
- Use time-decay attribution to understand channels closer to conversion.

## Recommendation
Do not make budget decisions from one model alone. Compare models, identify channels that are consistently strong, and investigate channels that are undervalued by last-touch reporting.
"""

    st.download_button(
        label="Download markdown action plan",
        data=action_plan,
        file_name="marketing_attribution_action_plan.md",
        mime="text/markdown"
    )

with tab4:
    st.subheader("Customer journey dataset")
    st.dataframe(df, use_container_width=True, hide_index=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download cleaned data",
        data=csv,
        file_name="customer_journey_data_cleaned.csv",
        mime="text/csv"
    )

st.caption("Built by Himanshu Jain — Marketing Analytics Portfolio Project")
