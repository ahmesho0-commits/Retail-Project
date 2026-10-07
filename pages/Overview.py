import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data, apply_shared_filters, apply_net_mode, style, page_header, kpis

df_all = load_data()
base, sel_years, net_mode = apply_shared_filters(df_all)
n = apply_net_mode(base, net_mode)

page_header("Business Overview", "High-level performance metrics and trends", base, net_mode)

# KPI CALCULATION
k = kpis(base if not net_mode else n)

prev = None
if len(sel_years) == 1 and (sel_years[0] - 1) in df_all.Order_Year.values:
    prev_base = df_all[
        (df_all['Order_Year'] == sel_years[0] - 1) &
        df_all['Country'].isin(base['Country'].unique()) &
        df_all['Product_Category'].isin(base['Product_Category'].unique()) &
        df_all['Sales_Channel'].isin(base['Sales_Channel'].unique())
    ]
    prev_n = apply_net_mode(prev_base, net_mode)
    prev = kpis(prev_base if not net_mode else prev_n)

def delta(key, pct=False):
    if prev is None or prev[key] == 0:
        return None
    return f"{(k[key] / prev[key] - 1) * 100:+.1f}%" if pct else f"{k[key] - prev[key]:+.1f}"

st.subheader(":material/monitoring: Performance")
with st.container(border=True):
    r1 = st.columns(4)
    r1[0].metric("Total Sales", f"{k['sales']:,.0f}", delta("sales", True))
    r1[1].metric("Total Profit", f"{k['profit']:,.0f}", delta("profit", True))
    r1[2].metric("Profit Margin", f"{k['margin']:.1f}%", delta("margin") and delta("margin") + " pts")
    r1[3].metric("Avg Order Value", f"{k['aov']:,.0f}", delta("aov", True))

    r2 = st.columns(4)
    r2[0].metric("Units Sold", f"{k['units']:,.0f}", delta("units", True))
    r2[1].metric("Return Rate (status)", f"{k['returns']:.1f}%", delta("returns") and delta("returns") + " pts", delta_color="inverse")
    r2[2].metric("Avg Rating", f"{k['rating']:.2f} / 5", delta("rating"))
    r2[3].metric("Avg Delivery Days", f"{k['delivery']:.2f}", delta("delivery"), delta_color="inverse")

rf = (base['Return_Flag'] == 'Yes').mean() * 100
if abs(rf - k['returns']) > 0.1:
    st.caption(f":material/info: Return flag column shows {rf:.1f}% returns vs {k['returns']:.1f}% by order status.")

# BUSINESS OVERVIEW CARDS
customers = n['Customer_ID'].nunique()
countries = n['Country'].nunique()
categories = n['Product_Category'].nunique()
avg_price = n['Unit_Price'].mean()

Best_Selling_Country = n.groupby('Country')['Sales_Amount'].sum().reset_index().sort_values(by='Sales_Amount', ascending=False)
Best_Selling_City = n.groupby('City')['Sales_Amount'].sum().reset_index().sort_values(by='Sales_Amount', ascending=False)
df_Representative = n.groupby('Sales_Representative')['Sales_Amount'].sum().reset_index().sort_values(by='Sales_Amount', ascending=False)

st.subheader(":material/public: Business Reach")
with st.container(border=True):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Served Customers", f"{customers:,}")
    c2.metric("Countries", countries)
    c3.metric("Product Categories", categories)
    c4.metric("Avg Product Price", f"{avg_price:,.2f}")

    b1, b2, b3 = st.columns(3)
    b1.metric("Best Selling Country", Best_Selling_Country.iloc[0]['Country'] if not Best_Selling_Country.empty else "N/A", f"{Best_Selling_Country.iloc[0]['Sales_Amount']:,.0f}" if not Best_Selling_Country.empty else "")
    b2.metric("Best Selling City", Best_Selling_City.iloc[0]['City'] if not Best_Selling_City.empty else "N/A", f"{Best_Selling_City.iloc[0]['Sales_Amount']:,.0f}" if not Best_Selling_City.empty else "")
    b3.metric("Best Sales Rep", df_Representative.iloc[0]['Sales_Representative'] if not df_Representative.empty else "N/A", f"{df_Representative.iloc[0]['Sales_Amount']:,.0f}" if not df_Representative.empty else "")

# CHARTS
st.subheader(":material/trending_up: Trends & Demographics")
c1, c2 = st.columns(2)

# Sales and Profit by Month
m = n.groupby("Month_Year", as_index=False).agg(Sales=("Sales_Amount", "sum"), Profit=("Profit", "sum"))
fig1 = px.line(m, x="Month_Year", y=["Sales", "Profit"], title="Monthly Sales & Profit")
c1.plotly_chart(style(fig1), width="stretch")

# Sales by Year
y = n.groupby("Order_Year", as_index=False).agg(Sales=("Sales_Amount", "sum"))
fig2 = px.bar(y, x="Order_Year", y="Sales", text_auto=".3s", title="Sales by Year")
fig2.update_xaxes(dtick=1)
c2.plotly_chart(style(fig2), width="stretch")

c3, c4 = st.columns(2)
# Margin by Category
cat = n.groupby("Product_Category", as_index=False).agg(Sales=("Sales_Amount", "sum"), Profit=("Profit", "sum"))
cat["Margin_%"] = cat["Profit"] / cat["Sales"] * 100
cat = cat.sort_values("Margin_%")
fig3 = px.bar(cat, x="Margin_%", y="Product_Category", orientation="h", text_auto=".1f", title="Profit Margin % by Category")
c3.plotly_chart(style(fig3), width="stretch")

# Sales by Channel
ch = n.groupby("Sales_Channel", as_index=False).agg(Sales=("Sales_Amount", "sum"))
fig4 = px.pie(ch, names="Sales_Channel", values="Sales", hole=0.5, title="Sales by Channel")
c4.plotly_chart(style(fig4), width="stretch")

st.subheader(":material/map: Geography")
g1, g2 = st.columns(2)
co = n.groupby("Country", as_index=False).agg(Sales=("Sales_Amount", "sum")).sort_values("Sales")
fig5 = px.bar(co, x="Sales", y="Country", orientation="h", text_auto=".3s", title="Sales by Country")
g1.plotly_chart(style(fig5), width="stretch")

fig6 = px.bar(Best_Selling_City.head(12), y='City', x='Sales_Amount', text_auto='.3s', title='Top Cities by Sales')
fig6.update_yaxes(autorange="reversed")
g2.plotly_chart(style(fig6), width="stretch")

# Extra Insight: Sales by Customer Segment
st.subheader(":material/group: Customer Segments")
seg = n.groupby("Customer_Segment", as_index=False).agg(Sales=("Sales_Amount", "sum")).sort_values("Sales")
fig7 = px.bar(seg, x="Sales", y="Customer_Segment", orientation="h", text_auto=".3s", title="Sales by Customer Segment")
st.plotly_chart(style(fig7), width="stretch")
