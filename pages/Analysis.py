import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px


st.set_page_config(page_title= 'Analysis', layout= 'wide')
html ="""
    <div style="text-align: center; color: white; font-size: 30px; font-weight: bold;">
        This is a centered Text
    </div>
    """
st.markdown(html, unsafe_allow_html= True)
df= pd.read_parquet('cleaned_data.parquet')

tab1,tab2 =st.tabs (['Numerical Analysis','Categorical Analysis'])

with tab1 :
    st.subheader('Numerical Analysis')
    
    numerical_cols = df.select_dtypes(include= 'number').columns 
    user_select=st.selectbox('Column',numerical_cols) 
    chart_select =st .radio('Chart',["Histogram","Box Plot"])

    if st.button('Show Chart',key=1):
        if chart_select == 'Histogram':
            st.plotly_chart(px.histogram (data_frame=df , x= user_select,title = user_select))
        else : 
            st.plotly_chart(px.box (data_frame=df , x= user_select,title=user_select))
with tab2 :
     st.subheader('Categorical Analysis')

     Categorical_column= df.select_dtypes(include= 'object').columns.drop(['Customer_ID', 'Customer_Name','Sales_Representative'])
     user_select_1 = st.selectbox ('Column',Categorical_column)
     chart_select_1 = st.radio('Chart' , ['Histogram','Pie'])
     if  st.button('Show Chart',key=2):
        if chart_select_1 == 'Histogram':
            st.plotly_chart(px.histogram (data_frame=df , x= user_select_1,title = user_select_1))
        else: 
            st.plotly_chart(px.pie(data_frame=df , names= user_select_1,title=user_select_1))
    