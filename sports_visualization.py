import streamlit as st
from multiapp import MultiApp

from yearly_statistics import yearly_statistics
from monthly_statistics import monthly_statistics
from time_spent import time_spent_moving_per_year
from yearly_comparison import yearly_comparison
from two_activities_one_year_comparison import two_activities_one_year_comparison
from evolution_of_time_spent_exercising import evolution_of_time_spent_exercising
from last_3_years_performance import last_3_years_performance

st.set_page_config(page_title='Sports Visualizations', layout='centered')

app = MultiApp()

app.add_app('Division of Time Spent', time_spent_moving_per_year)
app.add_app('Evolution of Time Spent', evolution_of_time_spent_exercising)
app.add_app('Last 3 Years Performance', last_3_years_performance)
app.add_app('Monthly Statistics', monthly_statistics)
app.add_app('Two Activities - One Year Comparison', two_activities_one_year_comparison)
app.add_app('Two Years - One Activity  Comparison', yearly_comparison)
app.add_app('Yearly Statistics', yearly_statistics)

app.run()