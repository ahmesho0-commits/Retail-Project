import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px


st.set_page_config(page_title= 'KPIS', layout= 'wide')
html ="""
    <div style="text-align: center; color: white; font-size: 30px; font-weight: bold;">
        Retail Data Analysis


    </div>
    """
st.markdown(html, unsafe_allow_html= True)
df= pd.read_parquet('cleaned_data.parquet')

df['Customer_Name'].nunique()
df['Country'].nunique()
df['Product_Category'].nunique()
df['Profit'].sum()
df['Unit_Price'].mean().round(2)

px.pie(data_frame= df, names= 'Product_Category', hole= 0.5 , title= 'Products Type')
Best_Selling_Country = df.groupby('Country')['Sales_Amount'].sum().reset_index().sort_values(by='Sales_Amount',ascending=False).reset_index(drop=True)
st.dataframe(Best_Selling_Country)

Best_Selling_Country.iloc[0]

Best_Selling_City = df.groupby('City')['Sales_Amount'].sum().reset_index().sort_values(by='Sales_Amount',ascending=False).reset_index(drop=True)
st.dataframe(Best_Selling_City)
px.bar(data_frame= Best_Selling_City, y= 'City', x= 'Sales_Amount', text_auto= True,
       labels= {'Sales_Amount' : 'Total Sales'},
       title= 'Sales Per City')
Best_Selling_City.iloc[0]

df_Representative= df.groupby('Sales_Representative')['Sales_Amount'].sum().reset_index().sort_values(by='Sales_Amount',ascending=False).reset_index(drop=True)
st.dataframe(df_Representative.head(3))
