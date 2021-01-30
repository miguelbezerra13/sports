import streamlit as st
from multiapp import MultiApp

from yearly_statistics import yearly_statistics
from monthly_statistics import monthly_statistics
from time_spent import time_spent_moving_per_year
from yearly_comparison import yearly_comparison

st.set_page_config(page_title='Sports Visualizations', layout='centered')

app = MultiApp()

app.add_app('Division of Time Spent', time_spent_moving_per_year)
app.add_app('Monthly Statistics', monthly_statistics)
app.add_app('Yearly Comparison', yearly_comparison)
app.add_app('Yearly Statistics', yearly_statistics)

app.run()