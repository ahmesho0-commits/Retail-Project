import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px


st.set_page_config(page_title= 'Customer Insights', layout= 'wide')
html ="""
    <div style="text-align: center; color: white; font-size: 30px; font-weight: bold;">
        This is a centered Text
    </div>
    """
st.markdown(html, unsafe_allow_html= True)
df= pd.read_parquet('cleaned_data.parquet')