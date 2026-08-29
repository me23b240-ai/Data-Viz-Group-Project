import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from style import inject_css, kpi_card, stamp, hero, styled_fig, QUADRANT_COLORS, FAILURE_TYPE_COLORS, RUST, WAYBILL, SEAL, ALERT, MANIFEST, MUTED

st.set_page_config(page_title="Marketplace Experience Dashboard", layout="wide")
inject_css()

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"

@st.cache_data
def load_data():
    master = pd.read_csv(DATA_DIR / "week1_master_order_table.csv")
    cat_metrics = pd.read_csv(DATA_DIR / "week1_category_metrics.csv")
    seller_metrics = pd.read_csv(DATA_DIR / "week1_seller_metrics.csv")
    state_metrics_w1 = pd.read_csv(DATA_DIR / "week1_state_metrics.csv")
    delay_buckets = pd.read_csv(DATA_DIR / "week1_delay_bucket_metrics.csv")
    seller_profiles = pd.read_csv(DATA_DIR / "week2_high_risk_seller_profiles.csv")
    seller_failure_summary = pd.read_csv(DATA_DIR / "week2_seller_failure_type_summary.csv")
    state_risk = pd.read_csv(DATA_DIR / "week2_state_risk_metrics.csv")
    geo_priority = pd.read_csv(DATA_DIR / "week2_geographic_priority_groups.csv")
    cat_failure = pd.read_csv(DATA_DIR / "week2_category_failure_type.csv")
    cat_risk = pd.read_csv(DATA_DIR / "week2_category_risk_matrix.csv")
    master["order_purchase_timestamp"] = pd.to_datetime(master["order_purchase_timestamp"], errors="coerce")
    return {
        "master": master, "cat_metrics": cat_metrics, "seller_metrics": seller_metrics,
        "state_metrics_w1": state_metrics_w1, "delay_buckets": delay_buckets,
        "seller_profiles": seller_profiles, "seller_failure_summary": seller_failure_summary,
        "state_risk": state_risk, "geo_priority": geo_priority,
        "cat_failure": cat_failure, "cat_risk": cat_risk,
    }

data = load_data()
master = data["master"]

st.sidebar.title("Marketplace Experience Dashboard")
page = st.sidebar.radio("Go to", [
    "Executive Overview", "Customer Experience & Delivery",
    "Marketplace Risk (Categories & Sellers)", "Geographic & Operational Risk"
])

st.sidebar.markdown("---")
st.sidebar.subheader("Filters")

min_date, max_date = master["order_purchase_timestamp"].min(), master["order_purchase_timestamp"].max()
date_range = st.sidebar.date_input("Order date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

all_categories = sorted(master["product_category_name_english"].dropna().unique())
selected_categories = st.sidebar.multiselect("Category (leave empty = all)", all_categories)

all_states = sorted(master["customer_state"].dropna().unique())
selected_states = st.sidebar.multiselect("Customer state (leave empty = all)", all_states)

filtered = master.copy()
if len(date_range) == 2:
    filtered = filtered[
        (filtered["order_purchase_timestamp"] >= pd.Timestamp(date_range[0])) &
        (filtered["order_purchase_timestamp"] <= pd.Timestamp(date_range[1]))
    ]
if selected_categories:
    filtered = filtered[filtered["product_category_name_english"].isin(selected_categories)]
if selected_states:
    filtered = filtered[filtered["customer_state"].isin(selected_states)]

delivered = filtered[filtered["order_status"] == "delivered"].dropna(subset=["delivery_days"])
reviewed = delivered.dropna(subset=["review_score"])

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing {len(filtered):,} orders ({len(reviewed):,} reviewed) after filters")

if page == "Executive Overview":
    hero("Executive Overview", "How can the marketplace grow without breaking the customer experience?")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi_card("Total Orders", f"{len(filtered):,}")
    with c2: kpi_card("Avg Review Score", f"{reviewed['review_score'].mean():.2f}" if len(reviewed) else "—")
    with c3:
        low_rate = reviewed["is_low_rating"].mean() if len(reviewed) else np.nan
        kpi_card("Low-Rating Rate", f"{low_rate*100:.1f}%" if not np.isnan(low_rate) else "—",
                  tone="bad" if (not np.isnan(low_rate) and low_rate > 0.128) else "good")
    with c4:
        late_rate = delivered["is_late"].mean() if len(delivered) else np.nan
        kpi_card("Late-Delivery Rate", f"{late_rate*100:.1f}%" if not np.isnan(late_rate) else "—",
                  tone="bad" if (not np.isnan(late_rate) and late_rate > 0.08) else "good")
    with c5: kpi_card("Total GMV Proxy", f"R$ {filtered['items_total_price'].sum():,.0f}")

    st.markdown("---")
    st.subheader("The central finding: satisfaction collapses at the delivery-promise threshold")
    db = data["delay_buckets"]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=db["delay_bucket"], y=db["avg_score"],
                          marker_color=[WAYBILL]*(len(db)//2) + [RUST]*(len(db) - len(db)//2),
                          text=db["avg_score"].round(2), textposition="outside"))
    fig.update_layout(yaxis_title="Average review score", xaxis_title="Delay bucket (relative to promised date)", showlegend=False)
    st.plotly_chart(styled_fig(fig), use_container_width=True)
    st.caption("Once an order crosses its promised delivery date, satisfaction drops sharply — not gradually.")

    st.markdown("---")
    st.subheader("Where risk is currently concentrated")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(stamp("CATEGORIES", "neutral"), unsafe_allow_html=True)
        n_intrinsic = (data["cat_failure"]["type"].str.contains("Type B", case=False, na=False)).sum()
        kpi_card("Intervene-First Categories", len(data["cat_risk"][data["cat_risk"]["quadrant"]=="Intervene First"]),
                  f"{n_intrinsic} confirmed intrinsic-risk")
    with col2:
        st.markdown(stamp("SELLERS", "neutral"), unsafe_allow_html=True)
        sfs = data["seller_failure_summary"]
        mixed_n = sfs.loc[sfs["failure_type"].str.contains("Mixed"), "n_sellers"].sum()
        kpi_card("High-Risk Sellers Profiled", int(sfs["n_sellers"].sum()), f"{mixed_n} Mixed-risk (highest impact/seller)")
    with col3:
        st.markdown(stamp("GEOGRAPHY", "neutral"), unsafe_allow_html=True)
        gp = data["geo_priority"]
        hshr = gp[gp["priority_group"]=="High Scale + High Risk"]
        sub = f"{hshr['share_of_marketplace_low_rating'].sum():.1f}% of marketplace low-rating orders" if len(hshr) else ""
        kpi_card("High Scale + High Risk States", int(hshr["n_states"].sum()) if len(hshr) else 0, sub)

elif page == "Customer Experience & Delivery":
    hero("Customer Experience & Delivery", "")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Review score distribution")
        score_dist = reviewed["review_score"].value_counts(normalize=True).sort_index() * 100
        colors_map = {1: ALERT, 2: RUST, 3: MUTED, 4: WAYBILL, 5: SEAL}
        fig = go.Figure(go.Bar(x=score_dist.index.astype(int), y=score_dist.values,
                          marker_color=[colors_map[s] for s in score_dist.index],
                          text=score_dist.round(1).astype(str) + "%", textposition="outside"))
        fig.update_layout(xaxis_title="Review score", yaxis_title="% of reviewed orders")
        st.plotly_chart(styled_fig(fig, height=380), use_container_width=True)
    with col2:
        st.subheader("Delay bucket vs. satisfaction")
        split_by = st.selectbox("Split by", ["None", "Same-state vs Cross-state", "Category (top 3 by volume)"])
        bins = [-np.inf, -14, -7, -3, 0, 3, 7, 14, np.inf]
        labels = ["<-14d", "-14to-7d", "-7to-3d", "-3to0d", "0to3d", "3to7d", "7to14d", ">14d"]
        rv = reviewed.copy()
        rv["delay_bucket"] = pd.cut(rv["delay_vs_estimate_days"], bins=bins, labels=labels)
        fig = go.Figure()
        if split_by == "None":
            g = rv.groupby("delay_bucket", observed=True)["review_score"].mean()
            fig.add_trace(go.Scatter(x=g.index.astype(str), y=g.values, mode="lines+markers", line=dict(color=WAYBILL)))
        elif split_by == "Same-state vs Cross-state":
            for val, label, color in [(True, "Same state", WAYBILL), (False, "Cross state", RUST)]:
                sub = rv[rv["same_state"] == val]
                g = sub.groupby("delay_bucket", observed=True)["review_score"].mean()
                fig.add_trace(go.Scatter(x=g.index.astype(str), y=g.values, mode="lines+markers", name=label, line=dict(color=color)))
        else:
            top3 = rv["product_category_name_english"].value_counts().head(3).index
            palette_cycle = [WAYBILL, RUST, SEAL]
            for cat, color in zip(top3, palette_cycle):
                sub = rv[rv["product_category_name_english"] == cat]
                g = sub.groupby("delay_bucket", observed=True)["review_score"].mean()
                fig.add_trace(go.Scatter(x=g.index.astype(str), y=g.values, mode="lines+markers", name=cat, line=dict(color=color)))
        fig.update_layout(xaxis_title="Delay bucket", yaxis_title="Average review score")
        st.plotly_chart(styled_fig(fig, height=380), use_container_width=True)

    st.markdown("---")
    st.subheader("Does lateness hurt more for expensive orders?")
    rv2 = reviewed.copy()
    rv2["value_tier"] = pd.qcut(rv2["items_total_price"], q=3, labels=["Low value", "Mid value", "High value"], duplicates="drop")
    pivot = rv2.groupby(["value_tier", "is_late"], observed=True)["review_score"].mean().unstack()
    fig = go.Figure()
    fig.add_trace(go.Bar(name="On time", x=pivot.index.astype(str), y=pivot.get(False, pd.Series()), marker_color=WAYBILL))
    fig.add_trace(go.Bar(name="Late", x=pivot.index.astype(str), y=pivot.get(True, pd.Series()), marker_color=RUST))
    fig.update_layout(barmode="group", yaxis_title="Average review score")
    st.plotly_chart(styled_fig(fig, height=380), use_container_width=True)

elif page == "Marketplace Risk (Categories & Sellers)":
    hero("Marketplace Risk: Categories & Sellers", "")
    tab1, tab2 = st.tabs(["Categories", "Sellers"])
    with tab1:
        st.subheader("Category Risk Map")
        cr = data["cat_risk"].merge(
            data["cat_failure"][["category", "ontime_low_rate", "late_low_rate", "type"]],
            left_on="product_category_name_english", right_on="category", how="left"
        )
        fig = px.scatter(cr, x="n_orders", y="low_rating_rate", size="revenue", color="quadrant",
            color_discrete_map=QUADRANT_COLORS, hover_name="product_category_name_english",
            hover_data={"low_rating_rate": ":.1%", "n_orders": True, "revenue": ":,.0f"},
            labels={"n_orders": "Order volume", "low_rating_rate": "Low-rating rate"})
        fig.update_layout(yaxis_tickformat=".0%")
        st.plotly_chart(styled_fig(fig, height=520), use_container_width=True)

        st.markdown(stamp("TIER 1 — DELIVERY-DRIVEN", "neutral") + stamp("TIER 2 — INTRINSIC", "critical"), unsafe_allow_html=True)
        intervene = cr[cr["quadrant"] == "Intervene First"].copy()
        intervene["tier"] = np.where(intervene["type"].str.contains("Type B", na=False),
                                      "Tier 2: Intrinsic (needs product/seller review)",
                                      "Tier 1: Delivery-driven (fix logistics)")
        st.dataframe(intervene[["product_category_name_english", "n_orders", "low_rating_rate",
                       "ontime_low_rate", "late_low_rate", "tier"]]
            .rename(columns={"product_category_name_english": "Category"}).sort_values("n_orders", ascending=False),
            use_container_width=True)

    with tab2:
        st.subheader("Seller Root-Cause Map")
        sp = data["seller_profiles"]
        fig = px.scatter(sp, x="late_delivery_rate", y="ontime_low_rate", size="low_rating_orders",
            color="failure_type", color_discrete_map=FAILURE_TYPE_COLORS,
            hover_data={"seller_id": True, "n_orders": True, "dominant_category": True},
            labels={"late_delivery_rate": "Late-delivery rate", "ontime_low_rate": "On-time low-rating rate"})
        fig.update_layout(xaxis_tickformat=".0%", yaxis_tickformat=".0%")
        st.plotly_chart(styled_fig(fig, height=520), use_container_width=True)

        st.markdown("**Business impact by failure type**")
        st.dataframe(data["seller_failure_summary"], use_container_width=True)

        ftype = st.selectbox("Failure type", sp["failure_type"].unique())
        st.dataframe(sp[sp["failure_type"] == ftype][
                ["seller_id", "n_orders", "overall_low_rate", "ontime_low_rate",
                 "late_delivery_rate", "dominant_category", "dominant_customer_state"]
            ].sort_values("n_orders", ascending=False), use_container_width=True)

elif page == "Geographic & Operational Risk":
    hero("Geographic & Operational Risk", "")
    st.subheader("Geographic Risk vs Scale Map")
    sr = data["state_risk"]
    fig = px.scatter(sr, x="n_orders", y="low_rating_rate", size="low_rating_orders", color="priority_group",
        color_discrete_map=QUADRANT_COLORS, text="customer_state",
        labels={"n_orders": "Order volume", "low_rating_rate": "Low-rating rate"})
    fig.update_traces(textposition="top center")
    fig.update_layout(yaxis_tickformat=".0%")
    st.plotly_chart(styled_fig(fig, height=550), use_container_width=True)

    st.markdown("---")
    st.subheader("Is geographic risk delivery-driven or intrinsic?")
    high_risk_states = sr[sr["priority_group"].isin(["High Scale + High Risk", "Low Scale + High Risk"])]
    high_risk_states = high_risk_states.sort_values("low_rating_rate", ascending=False)
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name="On-time low-rating rate", x=high_risk_states["customer_state"],
                           y=high_risk_states["low_rating_rate"], marker_color=MUTED))
    baseline = master.loc[master["is_late"] == False, "is_low_rating"].mean()
    fig2.add_hline(y=baseline, line_dash="dash", annotation_text="Marketplace on-time baseline", line_color=RUST)
    fig2.update_layout(yaxis_title="Low-rating rate", yaxis_tickformat=".0%")
    st.plotly_chart(styled_fig(fig2, height=420), use_container_width=True)
    st.caption("Every high-risk state's on-time performance sits close to the marketplace baseline — geographic risk is unanimously delivery-driven.")

    st.markdown("---")
    st.subheader("Business impact by geographic priority group")
    st.dataframe(data["geo_priority"], use_container_width=True)

    st.subheader("RJ + office_furniture: a compounding risk")
    rj_of = master[(master["customer_state"] == "RJ") & (master["product_category_name_english"] == "office_furniture")]
    rj_of_reviewed = rj_of.dropna(subset=["review_score"])
    if len(rj_of_reviewed):
        c1, c2, c3 = st.columns(3)
        with c1: kpi_card("RJ Overall Low-Rating", f"{sr.loc[sr['customer_state']=='RJ','low_rating_rate'].values[0]*100:.1f}%")
        with c2: kpi_card("office_furniture Overall Low-Rating", f"{data['cat_risk'].loc[data['cat_risk']['product_category_name_english']=='office_furniture','low_rating_rate'].values[0]*100:.1f}%")
        with c3: kpi_card("RJ + office_furniture Combined", f"{rj_of_reviewed['is_low_rating'].mean()*100:.1f}%", tone="bad")
