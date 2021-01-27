import streamlit as st

import numpy as np
import pandas as pd

from general_functions import create_color_time_spent_columns

from bokeh.models import ColumnDataSource, LabelSet
from bokeh.plotting import figure

def yearly_statistics():
    
    # Page title
    st.markdown("<h1 style='text-align: center;'>Yearly Statistics</h1>", unsafe_allow_html=True)
    
    # Load the dataframe
    df = pd.read_csv('rwc.csv', index_col=0, parse_dates=['Date'])
    
    # Variables to select the activity and the statistic
    
    col_1, col_2 = st.beta_columns(2)
    activity = col_1.selectbox('Activity:', sorted(df.Type.unique()))
    statistic = col_2.selectbox('Statistic:', ('Counter', 'Distance', 'Time'))
    
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
    
    # Set the source as the curated dataframe
    source = ColumnDataSource(activity_df)
    
    # Set the right counter name when the mouse hovers over the bars
    if activity == 'Running':
        counter_name = 'Number of runs'
    elif activity == 'Cycling':
        counter_name = 'Number of bike rides'
    else:
        counter_name = 'Number of walks'
    
    # Information when the mouse is hovered over the bars
    tooltips = [('Distance', "@Distance_km{0,0.00} km"), ('Time', "@time_spent"),
                ("Calories burned","@Calories{0,0}"), ("Cumulative Elevation Gain", "@ElevGain_m{0,0} m"),
                ("Average Speed", "@avg_speed{0.00} km/h"), (counter_name, "@count")]
    
    # Set the title and the y-axis label
    # If the chosen statistic was Time, the title will only change due to the activity. The label for the 
    # y-axis will always be Hours
    if statistic == 'Time':
        title = 'Amount of Time Spent '+activity # Adapt the title based on the activity
        label = 'Hours' # Y-axis label
    
    # If the chosen statistic is Distance, the title will be adjusted according to the activity, and the
    # y-axis label will be Kilometers
    elif statistic == 'Distance':
        if activity == 'Walking':
            verb = 'Walked'
        elif activity == 'Cycling':
            verb = 'Cycled'
        else:
            verb = 'Run'
        
        # As it happened for Time, the same procedure is applied to Distance
        title = 'Number of Kilometers '+verb+' per Year'
        label = 'Kilometers'
    
    else:
        title = counter_name+' per Year'
        label = counter_name
    
    # Instantiate the figure
    sports_fig = figure(title=title, x_axis_label='Year', y_axis_label = label, tooltips=tooltips,
                        plot_width=900, plot_height=500, tools='save', sizing_mode='scale_both')

    # Tweak the title
    sports_fig.title.align = 'center'
    sports_fig.title.text_font_size = "20px"

    # Remove unnecessary graph elements
    # Remove gridlines
    sports_fig.xgrid.grid_line_color, sports_fig.ygrid.grid_line_color = None, None

    # Remove x axis minor ticks
    sports_fig.xaxis.minor_tick_line_color = None
    
    # Remove outline line
    sports_fig.outline_line_color = None

    # Vertical bars
    # Set the bar height based on the chosen statistic and choose the data labels accordingly
    if statistic == 'Distance':
        label_choice = height_choice = 'Distance_km'
    elif statistic == 'Time':
        height_choice, label_choice = 'Time_h', 'time_spent'
    else:
        label_choice = height_choice = 'count'
    
    sports_fig.vbar(x='Year', top=height_choice, width=0.9, source=source, color='color')

    # Get the labels
    labels = LabelSet(x='Year', y=height_choice, text=label_choice, level='glyph', text_align='center',
                      source=source, render_mode='canvas', y_offset=3)

    # Add the labels to the figure
    sports_fig.add_layout(labels)

    # Show the figure
    st.bokeh_chart(sports_fig, True)