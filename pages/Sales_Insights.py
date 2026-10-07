import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data, apply_shared_filters, apply_net_mode, style, page_header

df_all = load_data()
base, sel_years, net_mode = apply_shared_filters(df_all)
df = apply_net_mode(base, net_mode)

page_header("Sales Insights", "Deep dive into sales trends, seasonality, and correlations", base, net_mode)

# EXTRA INSIGHT: Margin Trend by Month
st.subheader(":material/timeline: Yearly & Monthly Trends")
c1, c2 = st.columns(2)

sales_over_year = df.groupby('Order_Year')['Sales_Amount'].sum().reset_index()
fig_sales = px.line(sales_over_year, x='Order_Year', y='Sales_Amount', title='Sales Over Years', markers=True)
fig_sales.update_xaxes(dtick=1)
c1.plotly_chart(style(fig_sales), width="stretch")

df_Profit = df.groupby('Order_Year')['Profit'].sum().reset_index()
fig_profit = px.line(df_Profit, x='Order_Year', y='Profit', title='Profit Over Years', markers=True)
fig_profit.update_xaxes(dtick=1)
c2.plotly_chart(style(fig_profit), width="stretch")

# Extra: YoY growth table
growth = sales_over_year.copy()
growth["YoY Growth %"] = growth["Sales_Amount"].pct_change() * 100
with st.expander("Yearly table with growth"):
    st.dataframe(growth.round(1), hide_index=True)

# Extra Insight: Margin trend by month
st.subheader(":material/show_chart: Margin Trend by Month")
m = df.groupby("Month_Year", as_index=False).agg(Sales=("Sales_Amount", "sum"), Profit=("Profit", "sum"))
m["Margin_%"] = m["Profit"] / m["Sales"] * 100
fig_margin = px.line(m, x="Month_Year", y="Margin_%", title="Profit Margin Trend")
st.plotly_chart(style(fig_margin), width="stretch")

st.subheader(":material/category: Category & Channel Performance")
c3, c4 = st.columns(2)

df_category = df.groupby(['Product_Category', 'Order_Year'])['Sales_Amount'].sum().reset_index()
if not df_category.empty:
    most_selling_category = df_category.loc[df_category.groupby('Order_Year')['Sales_Amount'].idxmax()].reset_index(drop=True)
    fig_cat = px.bar(most_selling_category, y='Sales_Amount', x='Order_Year', text_auto='.3s',
                     color='Product_Category', title='Top Product Category Each Year')
    fig_cat.update_xaxes(dtick=1)
    c3.plotly_chart(style(fig_cat), width="stretch")

df_Sales_Channel = df.groupby('Sales_Channel')['Sales_Amount'].sum().reset_index().sort_values(by='Sales_Amount', ascending=False)
fig_ch = px.bar(df_Sales_Channel, y='Sales_Amount', x='Sales_Channel', text_auto='.3s', title='Sales Per Channel')
c4.plotly_chart(style(fig_ch), width="stretch")

st.subheader(":material/price_change: Discount vs Profit")
corr = df['Discount_Percentage'].corr(df['Profit']) if not df.empty else 0

st.markdown(f"<div class='insight'>Correlation between Discount and Profit is <b>{corr:.2f}</b>: "
            f"{'higher discounts go with lower profit per order.' if corr < -0.1 else 'the link between discount and profit is weak.'}"
            f"</div>", unsafe_allow_html=True)

fig_scatter = px.scatter(df, x='Discount_Percentage', y='Profit', trendline='ols',
                         trendline_color_override='#B45309', opacity=0.35,
                         title='Discount Percentage vs Profit')
st.plotly_chart(style(fig_scatter, 520), width="stretch")

st.subheader(":material/calendar_month: Seasonality")
df_month = df.groupby('month_name')['Sales_Amount'].sum().reset_index()
month_order = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"]
df_month['month_name'] = pd.Categorical(df_month['month_name'], categories=month_order, ordered=True)
df_month = df_month.sort_values('month_name')
df_month_sorted = df_month.sort_values('Sales_Amount', ascending=False)

if not df_month_sorted.empty:
    top3 = ", ".join(df_month_sorted.month_name.head(3))
    low2 = ", ".join(df_month_sorted.month_name.tail(2))
    st.markdown(f"<div class='insight'>Sales peak in <b>{top3}</b> and are lowest in <b>{low2}</b>.</div>", unsafe_allow_html=True)

fig_season = px.bar(df_month, x='month_name', y='Sales_Amount', text_auto='.3s', title='Sales by Month')
st.plotly_chart(style(fig_season), width="stretch")
