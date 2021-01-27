import streamlit as st

import numpy as np
import pandas as pd
from math import radians

from bokeh.models import ColumnDataSource, Label
from bokeh.plotting import figure
from bokeh.transform import cumsum

def time_spent_moving_per_year():
    
    # Page title
    st.markdown("<h1 style='text-align: center;'>Time Spent</h1>", unsafe_allow_html=True)
    
    # Load the dataframe
    df = pd.read_csv('rwc.csv', index_col=0, parse_dates=['Date'])
    
    # Get the years available
    year_options = df.Year.unique()
    
    year = st.slider('Year', int(min(year_options)), int(max(year_options)), step=1)
    
    # Select the data respective to that year, group it by type and sum it
    year_df = df.loc[df.Year==year].groupby('Type').sum()
    
    # Create a column for the labels of the time and for the colors of the sectors (red is running, green
    # is walking and blue is cycling)
    time_spent, color = [], []
    for activity in year_df.index:
        hours = int(year_df.Time_h[activity]) # Number of hours
        # Number of minutes, besides the hours already accounted
        minutes = int((year_df.Time_h[activity]-hours)*60) 
        
        # Format the number of minutes
        # When the number of minutes is between 1 and 9, add a 0 before it
        time = None
        if len(str(minutes)) == 1 and minutes != 0:
            minutes = '0'+str(minutes)
            
        # When the number of minutes is 0, the label is just the hours
        elif minutes == 0:
            time = str(hours) 
        
        if type(time) != str: # If time is already defined, this step will not be taken
            time = str(hours)+':'+str(minutes)+'\'' # Create the label
        
        time_spent.append(time) # Add the label to the list
        
        if activity == 'Running':
            color.append('red')
        
        elif activity == 'Walking':
            color.append('green')
            
        else:
            color.append('blue')
    
    year_df['time_spent'] = time_spent # Add the list as columns
    year_df['sector_color'] = color 
    
    # Add a column for the number of activities
    year_df['counter'] = df.loc[df.Year==year].groupby('Type').count()['Date']
    
    # Sort the dataframe by the value of the time in h
    year_df = year_df.sort_values(by='Time_h')
    
    # Percentage of time spent in each activity
    year_df['time_percentage'] = [year_df.Time_h[activity]/year_df.Time_h.sum() for activity in year_df.index]
    
    # Convert the percentages to radians
    year_df['graph_radians'] = [radians(year_df['time_percentage'][activity]*360) for activity in year_df.index]
    
    # Create a column for the labels of the percentage of time
    year_df['label_percentage'] = year_df['time_percentage']*100
    
    # =============================================================================
    # Plotting
    # =============================================================================
    
    # Set the source of the data
    source = ColumnDataSource(year_df)
    
    # Show the total amount of time spent
    summed = year_df.sum()['Time_h'] # Total amount of time in hours
    all_hours = int(summed)
    all_minutes = int((summed-all_hours)*60) # Same procedure as above
    
    all_time = None
    if len(str(all_minutes)) == 1 and all_minutes != 0:
        all_minutes = '0'+str(all_minutes)
            
        # When the number of minutes is 0, the label is just the hours
    elif all_minutes == 0:
        all_time = str(hours) 
        
    if type(all_time) != str: # If all_time is already defined, this step will not be taken
        all_time = str(all_hours)+':'+str(all_minutes)+'\'' # Create the label
    
    
    # Define the title
    title = 'Time Spent in Exercising Activities in '+str(year)+' - '+all_time
    
    # Set the tooltips
    tooltips = [('Distance', "@Distance_km{0,0.00} km"), ('Time', "@time_spent"),
                ('Percentage of Time Spent', "@label_percentage{0.00}%"),
                ("Calories burned","@Calories{0,0}"),
                ("Cumulative Elevation Gain", "@ElevGain_m{0,0} m"), 
                ('Number of activities', "@counter")]
    
    # Instantiate the figure
    time_pie = figure(plot_height=500, title=title, tools='hover, save', tooltips=tooltips,
                      x_range=(-0.65, 1.2), sizing_mode='scale_both')
    
    # Add the sectors
    time_pie.wedge(x=0, y=0, radius=0.6, start_angle=cumsum('graph_radians', include_zero=True),
                   end_angle=cumsum('graph_radians'), line_color='black', fill_color='sector_color',
                   legend_field='Type', source=source)
    
    # Tweak the title
    time_pie.title.align = 'center'
    time_pie.title.text_font_size = "20px"    

    # Hide the axes
    time_pie.axis.visible = False

    # Remove the gridlines
    time_pie.xgrid.grid_line_color, time_pie.ygrid.grid_line_color = None, None

    # Remove the outline
    time_pie.outline_line_color = None
    
    time_pie.legend.location = "center_right"
    
    # Show the figure
    st.bokeh_chart(time_pie, True)