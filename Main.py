import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px


st.set_page_config(page_title= 'Main', layout= 'wide')
html ="""
    <div style="text-align: center; color: white; font-size: 30px; font-weight: bold;">
        This is a centered Text
    </div>
    """
st.markdown(html, unsafe_allow_html= True)
df= pd.read_parquet('cleaned_data.parquet')
st.write('Retail Data Analysis')
st.subheader('Data Over View')

st.dataframe(df.head())
DESCRIPTIONS = {
    "Customer_Name": "Full name of the customer who placed the order.",
    "Customer_Age": "Age of the customer in years.",
    "Customer_Gender": "Gender of the customer (Male, Female, Non Binary).",
    "Customer_Segment": "Customer classification (Consumer, Corporate, Small Business, Premium, New Customer, Returning Customer).",
    "Order_Date": "Date the order was placed (YYYY-MM-DD).",
    "Sales_Channel": "Channel through which the order was made (Online, B2B Portal, Retail Store, Phone Order).",
    "Store_Name": "Store or location that fulfilled the order.",
    "Country": "Country where the order was placed.",
    "Region": "State / province / region within the country.",
    "City": "City where the order was placed.",
    "Product_Name": "Name of the product sold.",
    "Product_Category": "Top-level product group (Electronics, Furniture, Office Supplies, Appliances).",
    "Product_Subcategory": "Finer product grouping within the category (e.g. Cameras, Lighting, Paper).",
    "Quantity": "Number of units ordered.",
    "Unit_Price": "Price per unit before discount.",
    "Discount_Percentage": "Discount applied to the order, in percent.",
    "Sales_Amount": "Net revenue of the order: Quantity x Unit_Price x (1 - Discount).",
    "Cost_Amount": "Total cost of the goods sold for the order.",
    "Profit": "Sales_Amount minus Cost_Amount.",
    "Payment_Method": "How the customer paid (Credit Card, Debit Card, PayPal, Apple Pay, Cash, Bank Transfer).",
    "Order_Status": "Current order state (Completed, Shipped, Processing, Returned, Cancelled).",
    "Shipping_Method": "Delivery option chosen (Standard, Express, Next Day, Pickup).",
    "Delivery_Days": "Number of days between order and delivery.",
    "Return_Flag": "Whether the order was returned (Yes / No).",
    "Sales_Representative": "Sales rep who handled the order.",
    "Customer_Rating": "Customer satisfaction rating (scale 1 to 5).",
    "Inventory_Level": "Stock units on hand for the product at the time of the order.",
    "Order_Year": "Year extracted from Order_Date.",
    "month_name": "Month name extracted from Order_Date.",
}
id_cols = [c for c in df.columns if c.lower().endswith("id") or c.lower() == "id"]
cols = [c for c in df.columns if c not in id_cols]
def example(col):
    s = df[col].dropna()
    return str(s.iloc[0]) if len(s) else ""
 
table = pd.DataFrame(
    {
        "Column": cols,
        "Description": [DESCRIPTIONS.get(c, "No description yet.") for c in cols],
        "Unique Values": [df[c].nunique() for c in cols],
    }
)
 
st.caption(f"{len(df):,} rows | {len(cols)} columns shown | ID columns hidden: {', '.join(id_cols) or 'none'}")
 
search = st.text_input("Filter columns")
if search:
    mask = table["Column"].str.contains(search, case=False) | table["Description"].str.contains(search, case=False)
    table = table[mask]
 
st.dataframe(table, use_container_width=True, hide_index=True)
