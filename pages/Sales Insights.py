import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px


st.set_page_config(page_title= 'Sales Insights', layout= 'wide')
html ="""
    <div style="text-align: center; color: white; font-size: 30px; font-weight: bold;">
        This is a centered Text
    </div>
    """
st.markdown(html, unsafe_allow_html= True)
df= pd.read_parquet('cleaned_data.parquet')

# How do sales change over year giving suitable visualizations

df['order_year'] = df['Order_Date'].dt.year
sales_over_year = df.groupby('order_year')['Sales_Amount'].sum().reset_index()
fig=px.line(sales_over_year, x='order_year', y='Sales_Amount', title='Sales Over Years',markers=True)
fig.update_xaxes(dtick=1)
st.plotly_chart(fig,use_container_width=True)

df_Profit = df.groupby('Order_Year')['Profit'].sum().reset_index()
px.line(data_frame= df_Profit, x= 'Order_Year', y= 'Profit')


df_category=df.groupby(['Product_Category','Order_Year'])['Sales_Amount'].sum().reset_index()
most_selling_category =df_category.loc[df_category.groupby('Order_Year')['Sales_Amount'].idxmax()].reset_index(drop=True)
st.dataframe(most_selling_category)

df_Sales_Channel = df.groupby('Sales_Channel')['Sales_Amount'].sum().reset_index().sort_values(by='Sales_Amount',ascending=False).reset_index(drop=True)

px.bar(data_frame= df_Sales_Channel, y= 'Sales_Amount', x= 'Sales_Channel', text_auto= True,
       labels= {'Sales_Amount' : 'Total Sales'},
       title= 'Sales Per Channel')

df['Discount_Percentage'].corr(df['Profit'])
px.scatter(df, x= 'Discount_Percentage', y= 'Profit', trendline= 'ols', trendline_color_override= 'red',
           title= 'Discount_Percentage vs Profit' )


df_month=df.groupby('month_name')['Sales_Amount'].sum().reset_index().sort_values(by='Sales_Amount',ascending=False).reset_index(drop=True) 
st.dataframe(df_month.head())
st.write ('It Seems that Sales go up in winter')

df_Profit_Product = df.groupby('Product_Name')['Profit'].sum().reset_index().sort_values(by='Profit',ascending=False).reset_index(drop=True)
df_Profit_Product.head(10)
px.bar(data_frame= df_Profit_Product.head(10), y= 'Profit', x= 'Product_Name', text_auto= True,
       labels= {'Profit' : 'Total Profit'}, title= 'Top 10 Most Profitable Products')


