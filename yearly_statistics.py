import streamlit as st

import numpy as np
import pandas as pd

from general_functions import create_color_time_spent_columns, title_label_plot

from bokeh.models import ColumnDataSource, LabelSet
from bokeh.plotting import figure

def yearly_statistics():
    
    # Page title
    st.markdown("<h1 style='text-align: center;'>Yearly Statistics</h1>", unsafe_allow_html=True)
    
    # Load the dataframe
    df = pd.read_csv('rwc.csv', index_col=0, parse_dates=['Date'])
    
    # Variables to select the activity and the statistic
    
    col_1, col_2 = st.columns(2)
    activity = col_1.selectbox('Activity:', sorted(df.Type.unique()))
    statistic = col_2.selectbox('Statistic:', ('Count', 'Distance', 'Time'))
    
    #####################################################################################################
    # Data selection and curation
    #####################################################################################################
    
    # Limit the data you will consider based on the activity, group it by year and sum it
    activity_df = df.loc[df.Type==activity].groupby('Year').sum()
    
    # Round the decimal cases of the distance to 2 if the activity is not cycling, and to 0 if it is cycling
    if activity != 'Cycling':
        activity_df.Distance_km = activity_df.Distance_km.round(2)
    else:
        activity_df.Distance_km = activity_df.Distance_km.round(0)
    
    # Add the average speed column which needs to come from the grouped data by years but the mean is taken
    # instead of the sum. In this case, regardless of the activity, the number is rounded to 2 decimal cases
    activity_df['avg_speed'] = df.loc[df.Type==activity].groupby('Year').mean()['AvgSpeed_km/h'].round(2)
    
    # Add the counts column which comes from the grouped data by years and a counter is taken
    activity_df['count'] = df.loc[df.Type==activity].groupby('Year').count()['Date']
    
    # Create the color and the time label columns
    create_color_time_spent_columns(activity_df, statistic)
    
    #####################################################################################################
    # Plotting
    #####################################################################################################
    
    sports_fig, height_choice, label_choice, source = title_label_plot('yearly', activity, statistic, activity_df)
    
    height_choice

    # Get the labels
    labels = LabelSet(x='Year', y=height_choice, text=label_choice, level='glyph', text_align='center',
                      source=source, render_mode='canvas', y_offset=3)

    # Add the labels to the figure
    sports_fig.add_layout(labels)

    # Show the figure
    st.bokeh_chart(sports_fig, True)