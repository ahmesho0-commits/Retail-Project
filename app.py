import streamlit as st

st.set_page_config(page_title="Retail Dashboard", layout="wide", page_icon=":material/analytics:")

pg = st.navigation([
    st.Page("pages/KPI .py", title="KPIs (Legacy)", icon=":material/bar_chart:"),
    st.Page("pages/Overview.py", title="Overview", icon=":material/dashboard:"),
    st.Page("pages/Sales_Insights.py", title="Sales Insights", icon=":material/insights:"),
    st.Page("pages/Products.py", title="Products", icon=":material/inventory_2:"),
    st.Page("pages/Risk_and_Team.py", title="Risk and Team", icon=":material/groups:")
])

pg.run()
