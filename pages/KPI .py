import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
 
 
html = """
    <div style="text-align: center; font-size: 30px; font-weight: bold;">
        Retail Data Analysis
    </div>
    """
st.markdown(html, unsafe_allow_html=True)
 
 
# ======================= DATA =======================
@st.cache_data
def load():
    df = pd.read_csv("cleaned_data.csv", parse_dates=["Order_Date"])
    df["Month"] = df["Order_Date"].dt.to_period("M").dt.to_timestamp()
    return df
 
df = load()
 
 
# ======================= FILTERS (dropdowns with Select all) =======================
st.sidebar.header("Filters")
 
def pick(label, col):
    options = sorted(df[col].unique())
    with st.sidebar.expander(label):                       # collapsible drop-down
        select_all = st.checkbox("Select all", value=True, key=f"all_{col}")
        chosen = st.multiselect(label, options, default=options, key=f"ms_{col}",
                                disabled=select_all, label_visibility="collapsed")
    return options if select_all else chosen
 
sel_years = pick("Year", "Order_Year")
sel_country = pick("Country", "Country")
sel_cat = pick("Category", "Product_Category")
sel_channel = pick("Channel", "Sales_Channel")
net_mode = st.sidebar.checkbox("Net basis (exclude Cancelled & Returned)", value=True)
 
base = df[df.Country.isin(sel_country)
          & df.Product_Category.isin(sel_cat)
          & df.Sales_Channel.isin(sel_channel)]
cur = base[base.Order_Year.isin(sel_years)]
if cur.empty:
    st.warning("No data for the selected filters.")
    st.stop()
 
def net(d):
    return d[~d.Order_Status.isin(["Cancelled", "Returned"])] if net_mode else d
 
n = net(cur)  # every financial KPI and chart below uses this
 
 
# ======================= KPI CALCULATION =======================
def kpis(d):
    x = net(d)
    s, p = x.Sales_Amount.sum(), x.Profit.sum()
    return {
        "sales": s, "profit": p,
        "margin": p / s * 100 if s else 0,
        "units": x.Quantity.sum(),
        "aov": x.Sales_Amount.mean() if len(x) else 0,
        "returns": (d.Order_Status == "Returned").mean() * 100 if len(d) else 0,
        "rating": d.Customer_Rating.mean(),
        "delivery": d.Delivery_Days.mean(),
    }
 
k = kpis(cur)
 
# delta vs previous year only when exactly one year is selected
prev = None
if len(sel_years) == 1 and (sel_years[0] - 1) in base.Order_Year.values:
    prev = kpis(base[base.Order_Year == sel_years[0] - 1])
 
def delta(key, pct=False):
    if prev is None or prev[key] == 0:
        return None
    return f"{(k[key] / prev[key] - 1) * 100:+.1f}%" if pct else f"{k[key] - prev[key]:+.1f}"
 
 
# ======================= HELPERS =======================
def agg(d, by):
    g = d.groupby(by, as_index=False).agg(Sales=("Sales_Amount", "sum"),
                                          Profit=("Profit", "sum"),
                                          Units=("Quantity", "sum"))
    g["Margin_%"] = g.Profit / g.Sales * 100
    return g
 
def style(fig, h=400):
    fig.update_layout(height=h, margin=dict(l=10, r=10, t=50, b=10), legend_title=None)
    return fig
 
 
# ======================= KPI CARDS =======================
st.subheader("Performance")
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
 
basis = "Net of Cancelled & Returned orders" if net_mode else "All orders (gross)"
rf = (cur.Return_Flag == "Yes").mean() * 100
st.caption(f"Basis: {basis}. Return flag column shows {rf:.1f}% vs {k['returns']:.1f}% by order status: reconcile before reporting.")
 
 
# ======================= BUSINESS OVERVIEW CARDS =======================
### No.of Served customers
customers = n['Customer_Name'].nunique()
### No.of countries
countries = n['Country'].nunique()
### No. of Products dealing with
categories = n['Product_Category'].nunique()
##### Average Product Price
avg_price = n['Unit_Price'].mean().round(2)
 
#### Best selling Country
Best_Selling_Country = n.groupby('Country')['Sales_Amount'].sum().reset_index().sort_values(by='Sales_Amount', ascending=False).reset_index(drop=True)
##### Best Selling City
Best_Selling_City = n.groupby('City')['Sales_Amount'].sum().reset_index().sort_values(by='Sales_Amount', ascending=False).reset_index(drop=True)
#### Best Selling Representative
df_Representative = n.groupby('Sales_Representative')['Sales_Amount'].sum().reset_index().sort_values(by='Sales_Amount', ascending=False).reset_index(drop=True)
 
st.subheader("Business Overview")
with st.container(border=True):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Served Customers", f"{customers:,}")
    c2.metric("Countries", countries)
    c3.metric("Product Categories", categories)
    c4.metric("Avg Product Price", f"{avg_price:,.2f}")
 
    b1, b2, b3 = st.columns(3)
    b1.metric("Best Selling Country", Best_Selling_Country.iloc[0]['Country'], f"{Best_Selling_Country.iloc[0]['Sales_Amount']:,.0f}", delta_color="off")
    b2.metric("Best Selling City", Best_Selling_City.iloc[0]['City'], f"{Best_Selling_City.iloc[0]['Sales_Amount']:,.0f}", delta_color="off")
    b3.metric("Best Sales Rep", df_Representative.iloc[0]['Sales_Representative'], f"{df_Representative.iloc[0]['Sales_Amount']:,.0f}", delta_color="off")
 
st.divider()
 
 
# ======================= TABS =======================
tab_trend, tab_geo, tab_prod, tab_risk, tab_team = st.tabs(
    ["Trend", "Geography & Channel", "Products", "Risk", "Team"])
 
with tab_trend:
    m = agg(n, "Month")
    fig = px.line(m, x="Month", y=["Sales", "Profit"], title="Monthly Sales & Profit")
    st.plotly_chart(fig, width=700)
    c1, c2 = st.columns(2)
    y = agg(n, "Order_Year")
    c1.plotly_chart(style(px.bar(y, x="Order_Year", y="Sales", text_auto=".3s", title="Sales by Year")),
                    width=700)
    cat = agg(n, "Product_Category").sort_values("Margin_%")
    c2.plotly_chart(style(px.bar(cat, x="Margin_%", y="Product_Category", orientation="h",
                                 text_auto=".1f", title="Profit Margin % by Category")),
                    width=700)
 
with tab_geo:
    c1, c2 = st.columns(2)
    co = agg(n, "Country").sort_values("Sales")
    c1.plotly_chart(style(px.bar(co, x="Sales", y="Country", orientation="h",
                                 text_auto=".3s", title="Sales by Country")),
                    width=700)
    ch = agg(n, "Sales_Channel")
    c2.plotly_chart(style(px.pie(ch, names="Sales_Channel", values="Sales", hole=0.5,
                                 title="Sales by Channel")),
                    width=700)
 
    fig_city = px.bar(data_frame=Best_Selling_City, y='City', x='Sales_Amount', text_auto=True,
                      labels={'Sales_Amount': 'Total Sales'},
                      title='Sales Per City')
    fig_city.update_yaxes(autorange="reversed")  # biggest city on top
    st.plotly_chart(style(fig_city, 450), width=700)
 
    with st.expander("Country table"):
        st.dataframe(co.sort_values("Sales", ascending=False).round(1), width=700, hide_index=True)
 
with tab_prod:
    p = agg(n, "Product_Name")
    c1, c2, c3 = st.columns([1, 1.5, 1.5])
    ### products
    c1.plotly_chart(style(px.pie(data_frame=n, names='Product_Category', hole=0.5, title='Products Type')),
                    width=700)
    top = p.nlargest(10, "Profit").sort_values("Profit")
    bot = p.nsmallest(10, "Profit").sort_values("Profit", ascending=False)
    c2.plotly_chart(style(px.bar(top, x="Profit", y="Product_Name", orientation="h",
                                 text_auto=".3s", title="Top 10 Products by Profit")),
                    width=700)
    c3.plotly_chart(style(px.bar(bot, x="Profit", y="Product_Name", orientation="h",
                                 text_auto=".3s", title="Bottom 10 Products by Profit")),
                    width=700)
    with st.expander("Product table"):
        st.dataframe(p.sort_values("Profit", ascending=False).round(1), width=700, hide_index=True)
 
with tab_risk:
    c1, c2 = st.columns(2)
    st_mix = cur.Order_Status.value_counts().reset_index()
    st_mix.columns = ["Order_Status", "Orders"]
    c1.plotly_chart(style(px.pie(st_mix, names="Order_Status", values="Orders", hole=0.5,
                                 title="Order Status Mix (all orders)")),
                    width=700)
 
    bands = pd.cut(n.Discount_Percentage, [-0.1, 0, 5, 10, 20, 100],
                   labels=["0%", "1-5%", "6-10%", "11-20%", ">20%"])
    d = n.assign(Band=bands).groupby("Band", observed=True, as_index=False).agg(
        Sales=("Sales_Amount", "sum"), Profit=("Profit", "sum"))
    d["Margin_%"] = d.Profit / d.Sales * 100
    c2.plotly_chart(style(px.bar(d, x="Band", y="Margin_%", text_auto=".1f",
                                 title="Profit Margin % by Discount Band")),
                    width=700)
 
    loss = n[n.Profit < 0]
    st.metric("Loss-making orders", f"{len(loss):,}", f"{len(loss) / len(n) * 100:.1f}% of orders",
              delta_color="off")
    st.dataframe(loss.nsmallest(15, "Profit")[["Order_Date", "Product_Name", "Country", "Sales_Channel",
                                               "Discount_Percentage", "Sales_Amount", "Profit"]],
                 width=700, hide_index=True)
 
with tab_team:
    rep = agg(n, "Sales_Representative").sort_values("Sales")
    left, right = st.columns([2, 1])
    fig = px.bar(rep, x="Sales", y="Sales_Representative", orientation="h",
                 color="Margin_%", text_auto=".3s", title="Sales Rep Leaderboard (color = margin %)")
    left.plotly_chart(style(fig, 550), width=700)
    with right:
        st.subheader("Top 3 Representatives")
        st.dataframe(df_Representative.head(3), hide_index=True, width=700)
 
 
st.sidebar.download_button("Download filtered data (CSV)", cur.to_csv(index=False), "filtered_data.csv")
 