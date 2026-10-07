import streamlit as st
import pandas as pd
import plotly.express as px
import statsmodels.api as sm

@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_data.csv", parse_dates=["Order_Date"])
    # Create Month for time series if needed, but Order_Date is fine. We can add a 'Month_Year'
    df["Month_Year"] = df["Order_Date"].dt.to_period("M").dt.to_timestamp()
    return df

def apply_shared_filters(df):
    st.sidebar.header("Filters")
    
    def pick(label, col):
        # Using session state to persist across pages if needed, but simple rerun works fine in Streamlit too
        options = sorted(df[col].dropna().unique())
        with st.sidebar.expander(label):
            select_all = st.checkbox("Select all", value=True, key=f"all_{col}")
            chosen = st.multiselect(label, options, default=options, key=f"ms_{col}",
                                    disabled=select_all, label_visibility="collapsed")
        return options if select_all else chosen

    sel_years = pick("Year", "Order_Year")
    sel_country = pick("Country", "Country")
    sel_cat = pick("Category", "Product_Category")
    sel_channel = pick("Channel", "Sales_Channel")
    net_mode = st.sidebar.toggle("Net basis (exclude Cancelled & Returned)", value=True)

    base = df[
        df['Order_Year'].isin(sel_years) &
        df['Country'].isin(sel_country) &
        df['Product_Category'].isin(sel_cat) &
        df['Sales_Channel'].isin(sel_channel)
    ]
    
    if base.empty:
        st.warning("No data for the selected filters.")
        st.stop()
        
    return base, sel_years, net_mode

def apply_net_mode(df, net_mode):
    if net_mode:
        return df[~df['Order_Status'].isin(["Cancelled", "Returned"])]
    return df

def style(fig, height=400):
    fig.update_layout(
        height=height, 
        margin=dict(l=10, r=10, t=50, b=10),
        legend_title=None,
        template="plotly_white",
        font=dict(size=13, color="#0F172A", family="sans serif"),
        title_font=dict(size=16, color="#0F172A", family="sans serif"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        title_x=0.0
    )
    fig.update_layout(colorway=["#0F766E", "#14B8A6", "#5EEAD4", "#334155", "#64748B", "#CBD5E1"])
    fig.update_xaxes(showgrid=True, gridcolor="#E2E8F0", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#E2E8F0", zeroline=False)
    return fig

def inject_styles():
    try:
        with open("assets/styles.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

def page_header(title, description, base_df, net_mode):
    inject_styles()
    st.markdown(f"""
    <div class="page-header">
        <h1>{title}</h1>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)
    basis = "Net of Cancelled & Returned orders" if net_mode else "All orders (gross)"
    st.caption(f"Active Filters: {len(base_df):,} rows | Basis: {basis}")

def kpis(d):
    s, p = d.Sales_Amount.sum(), d.Profit.sum()
    return {
        "sales": s, "profit": p,
        "margin": p / s * 100 if s else 0,
        "units": d.Quantity.sum(),
        "aov": d.Sales_Amount.mean() if len(d) else 0,
        "returns": (d.Order_Status == "Returned").mean() * 100 if len(d) else 0,
        "rating": d.Customer_Rating.mean() if len(d) else 0,
        "delivery": d.Delivery_Days.mean() if len(d) else 0,
    }
