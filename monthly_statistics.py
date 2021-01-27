import streamlit as st

import numpy as np
import pandas as pd

from general_functions import create_color_time_spent_columns, title_label_plot

from bokeh.models import ColumnDataSource, LabelSet
from bokeh.models.tickers import FixedTicker
from bokeh.plotting import figure

def monthly_statistics():
    
    # Page title
    st.markdown("<h1 style='text-align: center;'>Monthly Statistics</h1>", unsafe_allow_html=True)
    
    # Load the dataframe
    df = pd.read_csv('rwc.csv', index_col=0, parse_dates=['Date'])
    
    col_1, col_2, col_3 = st.beta_columns(3)
    
    # Variables to select the activity, the statistic and the year
    activity = col_1.selectbox('Activity:', sorted(df.Type.unique()))
    statistic = col_2.selectbox('Statistic:', ['Counter', 'Distance', 'Time'])
    
    # The available years are conditioned to the selected activity
    year_options = df.loc[df.Type==activity].Year.unique()
    
    year = col_3.slider('Year', int(min(year_options)), int(max(year_options)), step=1)
        
    #####################################################################################################
    # Data selection and curation
    #####################################################################################################
    
    # Limit the data to be considered, based on the activity and the year, group it by month and sum it
    activity_df = df.loc[df.Type==activity].loc[df.Year==year].groupby('Month').sum()
    
    # Round the decimal cases of the distance to 2
    activity_df.Distance_km = activity_df.Distance_km.round(2)    
    
    # Add the average speed column which needs to come from the grouped data by month but the mean is taken
    # instead of the sum, rounded to 2 decimal cases
    activity_df['avg_speed'] = df.loc[df.Type==activity].loc[df.Year==year].groupby('Month').mean()['AvgSpeed_km/h'].round(2)
    
    # Add the counts column which comes from the grouped data by years and a counter is taken
    activity_df['count'] = df.loc[df.Type==activity].loc[df.Year==year].groupby('Month').count()['Date']
    
    # Create the color and the time label columns
    create_color_time_spent_columns(activity_df, statistic)
    
    # As there are some months in which some of the activities were not done and they should "appear" in the
    # graph, it is necessary to create rows for them
    
    # Variable to store the values for a row without any activity
    no_activity_row = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, None, None]
    
    for month in range(1,13): # Loop over the months
        # If there were activities during the month, nothing needs to be done
        if month in activity_df.index:
            pass
        # Add the no activity row if there were any activities
        else:
            activity_df.loc[month] = no_activity_row
    
    # Sort the index of the dataframe
    activity_df = activity_df.sort_index()
    
    #####################################################################################################
    # Plotting
    #####################################################################################################
    
    sports_fig, height_choice, label_choice = title_label_plot('monthly', activity,
                                                                       statistic, activity_df,
                                                                       year)[:-1]
    
    # Change the x_ticks to the names of the months
    x_ticks_dict = {}
    month_name = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for month in activity_df.index:
        x_ticks_dict[month] = month_name[month-1]

    sports_fig.xaxis.ticker = FixedTicker(ticks=activity_df.index) # Show all the months as x-ticks
    sports_fig.xaxis.major_label_overrides = x_ticks_dict # Override the x-tick labels
        
    # Get the labels - it is necessary to have a "new" source without NaN values
    new_source=ColumnDataSource(activity_df.dropna())
    
    labels = LabelSet(x='Month', y=height_choice, text=label_choice, level='glyph', text_align='center',
                      source=new_source, render_mode='canvas', y_offset=3, text_font_size='10pt')
    
    # Add the labels to the figure
    sports_fig.add_layout(labels)

    # Show the figure
    st.bokeh_chart(sports_fig, True)