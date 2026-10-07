import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
 
st.set_page_config(page_title='Sales Insights', layout='wide')
 
# ======================= STYLE =======================
st.markdown("""
<style>
    .block-container {padding-top: 1.5rem;}
    .hero {text-align:center; padding:18px 10px; border-radius:14px; margin-bottom:12px;
           background: linear-gradient(90deg, #1f4e79, #2e86c1); color:white;}
    .hero h1 {margin:0; font-size:32px; font-weight:700; color:white;}
    .hero p {margin:4px 0 0 0; opacity:.85;}
    [data-testid="stMetric"] {background: rgba(128,128,128,.10); border-radius:12px; padding:12px 16px;}
    .insight {border-left:5px solid #2e86c1; background:rgba(46,134,193,.10);
              padding:10px 14px; border-radius:6px; margin:6px 0 12px 0;}
</style>
<div class="hero">
    <h1>Sales Insights</h1>
    <p>Yearly trends, categories, channels, discounts, seasonality and products</p>
</div>
""", unsafe_allow_html=True)
 
 
# ======================= DATA =======================
@st.cache_data
def load():
    return pd.read_csv('cleaned_data.csv', parse_dates=['Order_Date'])
 
df_all = load()
 
 
# ======================= FILTERS =======================
st.sidebar.header("Filters")
 
def pick(label, col):
    options = sorted(df_all[col].unique())
    with st.sidebar.expander(label):
        select_all = st.checkbox("Select all", value=True, key=f"all_{col}")
        chosen = st.multiselect(label, options, default=options, key=f"ms_{col}",
                                disabled=select_all, label_visibility="collapsed")
    return options if select_all else chosen
 
sel_years = pick("Year", "Order_Year")
sel_country = pick("Country", "Country")
sel_cat = pick("Category", "Product_Category")
sel_channel = pick("Channel", "Sales_Channel")
net_mode = st.sidebar.checkbox("Net basis (exclude Cancelled & Returned)", value=True)
 
df = df_all[df_all.Order_Year.isin(sel_years)
            & df_all.Country.isin(sel_country)
            & df_all.Product_Category.isin(sel_cat)
            & df_all.Sales_Channel.isin(sel_channel)]
if net_mode:
    df = df[~df.Order_Status.isin(["Cancelled", "Returned"])]
if df.empty:
    st.warning("No data for the selected filters.")
    st.stop()
 
def style(fig, h=420):
    fig.update_layout(height=h, margin=dict(l=10, r=10, t=55, b=10), legend_title=None)
    return fig
 
 
# ======================= HEADLINE KPIs =======================
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Sales", f"{df.Sales_Amount.sum():,.0f}")
k2.metric("Total Profit", f"{df.Profit.sum():,.0f}")
k3.metric("Profit Margin", f"{df.Profit.sum() / df.Sales_Amount.sum() * 100:.1f}%")
k4.metric("Orders", f"{len(df):,}")
 
basis = "Net of Cancelled & Returned orders" if net_mode else "All orders (gross)"
st.caption(f"Basis: {basis}")
 
tab_year, tab_cat, tab_disc, tab_season, tab_prod = st.tabs(
    ["Yearly Trend", "Category & Channel", "Discount vs Profit", "Seasonality", "Products"])
 
 
# ======================= YEARLY TREND =======================
with tab_year:
    st.subheader("How do sales change over the years?")
    sales_over_year = df.groupby('Order_Year')['Sales_Amount'].sum().reset_index()
    ### Profit / Year
    df_Profit = df.groupby('Order_Year')['Profit'].sum().reset_index()
 
    c1, c2 = st.columns(2)
    fig = px.line(sales_over_year, x='Order_Year', y='Sales_Amount', title='Sales Over Years', markers=True)
    fig.update_xaxes(dtick=1)
    c1.plotly_chart(style(fig), use_container_width=True )
 
    fig = px.line(data_frame=df_Profit, x='Order_Year', y='Profit', title='Profit Over Years', markers=True)
    fig.update_xaxes(dtick=1)
    c2.plotly_chart(style(fig), use_container_width=True )
 
    growth = sales_over_year.assign(**{"YoY Growth %": sales_over_year.Sales_Amount.pct_change() * 100}).round(1)
    with st.expander("Yearly table with growth"):
        st.dataframe(growth, hide_index=True, use_container_width=True )
 
 
# ======================= CATEGORY & CHANNEL =======================
with tab_cat:
    c1, c2 = st.columns(2)
 
    ## Most Selling Category in each year
    df_category = df.groupby(['Product_Category', 'Order_Year'])['Sales_Amount'].sum().reset_index()
    most_selling_category = df_category.loc[df_category.groupby('Order_Year')['Sales_Amount'].idxmax()].reset_index(drop=True)
    fig_cat = px.bar(data_frame=most_selling_category, y='Sales_Amount', x='Order_Year', text_auto='.3s',
                     color='Product_Category',
                     labels={'Sales_Amount': 'Total Sales'},
                     title='Top Product Category each year')
    fig_cat.update_xaxes(dtick=1)
    c1.plotly_chart(style(fig_cat), use_container_width=True )
 
    ### Best Selling Sales Channel
    df_Sales_Channel = df.groupby('Sales_Channel')['Sales_Amount'].sum().reset_index().sort_values(by='Sales_Amount', ascending=False).reset_index(drop=True)
    fig_ch = px.bar(data_frame=df_Sales_Channel, y='Sales_Amount', x='Sales_Channel', text_auto='.3s',
                    labels={'Sales_Amount': 'Total Sales'},
                    title='Sales Per Channel')
    c2.plotly_chart(style(fig_ch), use_container_width=True )
 
    with st.expander("Top category per year (table)"):
        st.dataframe(most_selling_category, hide_index=True, use_container_width=True )
 
 
# ======================= DISCOUNT vs PROFIT =======================
with tab_disc:
    st.subheader("Discount relation with profit")
    df_percentage_Profit = df[['Discount_Percentage', 'Profit']]
    corr_df = df_percentage_Profit.corr(numeric_only=True).round(2)
    corr = df['Discount_Percentage'].corr(df['Profit'])
 
    m1, m2 = st.columns([1, 3])
    m1.metric("Correlation (Discount vs Profit)", f"{corr:.2f}")
    m2.markdown(
        f"<div class='insight'>Correlation is <b>{corr:.2f}</b>: "
        f"{'higher discounts go with lower profit per order.' if corr < -0.1 else 'the link between discount and profit is weak.'}"
        f"</div>", unsafe_allow_html=True)
 
    fig = px.scatter(df, x='Discount_Percentage', y='Profit', trendline='ols',
                     trendline_color_override='red', opacity=0.35,
                     title='Discount_Percentage vs Profit')
    st.plotly_chart(style(fig, 520), use_container_width=True )
 
    with st.expander("Correlation matrix"):
        st.plotly_chart(style(px.imshow(corr_df, text_auto=True), 350), use_container_width=True )
 
 
# ======================= SEASONALITY =======================
with tab_season:
    st.subheader("Are there seasonal sales patterns?")
    df_month = df.groupby('month_name')['Sales_Amount'].sum().reset_index().sort_values(by='Sales_Amount', ascending=False).reset_index(drop=True)
 
    month_order = ["January", "February", "March", "April", "May", "June", "July",
                   "August", "September", "October", "November", "December"]
    top3 = ", ".join(df_month.month_name.head(3))
    low2 = ", ".join(df_month.month_name.tail(2))
    st.markdown(f"<div class='insight'>Sales peak in <b>{top3}</b> and are lowest in <b>{low2}</b>.</div>",
                unsafe_allow_html=True)
 
    c1, c2 = st.columns([2, 1])
    monthly = df_month.set_index('month_name').reindex(month_order).reset_index()
    fig = px.bar(monthly, x='month_name', y='Sales_Amount', text_auto='.3s',
                 color='Sales_Amount', color_continuous_scale='Blues',
                 labels={'month_name': 'Month', 'Sales_Amount': 'Total Sales'},
                 title='Sales by Month')
    fig.update_layout(coloraxis_showscale=False)
    c1.plotly_chart(style(fig), use_container_width=True )
    c2.markdown("**Top 5 months**")
    c2.dataframe(df_month.head(), hide_index=True, use_container_width=True )
 
 
# ======================= PRODUCTS =======================
with tab_prod:
    #### What are the most profitable products?
    df_Profit_Product = df.groupby('Product_Name')['Profit'].sum().reset_index().sort_values(by='Profit', ascending=False).reset_index(drop=True)
    fig = px.bar(data_frame=df_Profit_Product.head(10), y='Profit', x='Product_Name', text_auto='.3s',
                 labels={'Profit': 'Total Profit'}, title='Top 10 Most Profitable Products')
    st.plotly_chart(style(fig), use_container_width=True )
 
    #### Quantity and sales / product
    prod = (
        df.groupby(["Product_Name", "Product_Category"], as_index=False)
        .agg(Quantity=("Quantity", "sum"),
             Sales=("Sales_Amount", "sum"),
             Profit=("Profit", "sum"),
             Avg_Discount=("Discount_Percentage", "mean"))
    )
    prod["Margin_%"] = prod["Profit"] / prod["Sales"] * 100
 
    fig = px.scatter(
        prod,
        x="Quantity",
        y="Margin_%",
        size="Sales",
        color="Product_Category",
        hover_name="Product_Name",
        hover_data={"Avg_Discount": ":.1f", "Profit": ":,.0f", "Sales": ":,.0f"},
        text="Product_Name",
        size_max=55,
        title="Volume vs Profit Margin per Product (bubble = sales)",
    )
    fig.update_traces(textposition="top center")
    # reference lines at the averages split the chart into 4 quadrants
    fig.add_hline(y=prod["Margin_%"].mean(), line_dash="dash", line_color="gray")
    fig.add_vline(x=prod["Quantity"].mean(), line_dash="dash", line_color="gray")
    fig.update_layout(xaxis_title="Total Quantity Sold", yaxis_title="Profit Margin (%)")
    st.plotly_chart(style(fig, 700), width="stretch")
 