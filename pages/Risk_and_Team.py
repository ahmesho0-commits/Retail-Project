import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data, apply_shared_filters, apply_net_mode, style, page_header

df_all = load_data()
# Note: For risk, we need the base without net_mode applied to show Order Status mix properly.
# We will use base for Order Status, but apply net_mode for the rest of financials.
base, sel_years, net_mode = apply_shared_filters(df_all)
df = apply_net_mode(base, net_mode)

page_header("Risk and Team", "Order risks, discounts, and sales team performance", base, net_mode)

st.subheader(":material/warning: Order Risks & Discounts")
c1, c2 = st.columns(2)

st_mix = base.Order_Status.value_counts().reset_index()
st_mix.columns = ["Order_Status", "Orders"]
fig_mix = px.pie(st_mix, names="Order_Status", values="Orders", hole=0.5, title="Order Status Mix (All Selected Orders)")
c1.plotly_chart(style(fig_mix), width="stretch")

bands = pd.cut(df.Discount_Percentage, [-0.1, 0, 5, 10, 20, 100], labels=["0%", "1-5%", "6-10%", "11-20%", ">20%"])
d = df.assign(Band=bands).groupby("Band", observed=True, as_index=False).agg(Sales=("Sales_Amount", "sum"), Profit=("Profit", "sum"))
d["Margin_%"] = d["Profit"] / d["Sales"] * 100
fig_band = px.bar(d, x="Band", y="Margin_%", text_auto=".1f", title="Profit Margin % by Discount Band")
c2.plotly_chart(style(fig_band), width="stretch")

loss = df[df.Profit < 0]
st.metric("Loss-making orders", f"{len(loss):,}", f"{len(loss) / len(df) * 100:.1f}% of orders" if len(df) else "0%", delta_color="off")
with st.expander("View Loss-making Orders"):
    st.dataframe(loss.nsmallest(15, "Profit")[["Order_Date", "Product_Name", "Country", "Sales_Channel",
                                               "Discount_Percentage", "Sales_Amount", "Profit"]],
                 hide_index=True, use_container_width=True)

st.subheader(":material/local_shipping: Shipping Performance")
ship = df.groupby("Shipping_Method", as_index=False).agg(Avg_Delivery_Days=("Delivery_Days", "mean")).sort_values("Avg_Delivery_Days")
fig_ship = px.bar(ship, x="Avg_Delivery_Days", y="Shipping_Method", orientation="h", text_auto=".1f", title="Average Delivery Days by Shipping Method")
st.plotly_chart(style(fig_ship), width="stretch")

st.subheader(":material/groups: Sales Team Performance")
rep = df.groupby("Sales_Representative", as_index=False).agg(Sales=("Sales_Amount", "sum"), Profit=("Profit", "sum")).sort_values("Sales")
rep["Margin_%"] = rep["Profit"] / rep["Sales"] * 100

left, right = st.columns([2, 1])
fig_rep = px.bar(rep, x="Sales", y="Sales_Representative", orientation="h", color="Margin_%", text_auto=".3s", title="Sales Rep Leaderboard (color = margin %)")
left.plotly_chart(style(fig_rep, 550), width="stretch")

with right:
    st.markdown("**Top 3 Representatives**")
    st.dataframe(rep.sort_values("Sales", ascending=False).head(3)[["Sales_Representative", "Sales"]], hide_index=True, use_container_width=True)
