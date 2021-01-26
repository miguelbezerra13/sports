import streamlit as st

import numpy as np
import pandas as pd

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
    
    # Create a column with the colors of the bars. Green is the smallest, red the biggest and blue are the
    # others. Create also the time labels
    
    color, time_spent = [], [] # Variable to hold the colors and the time labels
    
    for month in activity_df.index: # Loop over the months as they are the indices
        
        # Make sure the colors of the bars are set according to the statistic chosen
        if statistic == 'Distance':
            to_check = activity_df.Distance_km
        elif statistic == 'Time':
            to_check = activity_df.Time_h
        elif statistic == 'Counter':
            to_check = activity_df['count']
    
        # Add the color to the list
        if to_check[month] == max(to_check):
            color.append('red')
        elif to_check[month] == min(to_check):
            color.append('green')
        else:
            color.append('blue')
        
        # Create the time labels
        hour = int(activity_df.Time_h[month]) # The integer part is the number of hours spent
        
        # By removing the integer part to the overall value, you get the minutes, which need to be multiplied
        # by 60 and then rounded to no decimal cases
        minutes = int(round((activity_df.Time_h[month]-hour)*60, 0)) 
        
        # Format the number of minutes
        # When the number of minutes is between 1 and 9, add a 0 before it
        time = None
        if len(str(minutes)) == 1 and minutes != 0:
            minutes = '0'+str(minutes)
            
        # When the number of minutes is 0, the label is just the hours
        elif minutes == 0:
            time = str(hour) 
            
        if type(time) != str: # If time is already defined, this step will not be taken
            time = str(hour)+':'+str(minutes)+'\'' # Create the label
        
        time_spent.append(time) # Add the label to the list

    # Add the columns to the dataframe
    activity_df['color'] = color
    activity_df['time_spent'] = time_spent
    
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
        title = 'Amount of Time Spent '+activity+'in '+str(year) # Adapt the title based on the activity
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
        title = 'Number of Kilometers '+verb+' per Month in '+str(year)
        label = 'Kilometers'
    
    else:
        title = counter_name+' per Month in '+str(year)
        label = counter_name
    
    # Instantiate the figure
    sports_fig = figure(title=title, x_axis_label='Month', y_axis_label=label, tooltips=tooltips,
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
    
    # Change the x_ticks to the names of the months
    x_ticks_dict = {} # Dictionary that will hold the old and the new values for the x-ticks
    
    # List with the names of the months
    month_name = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    # Assign the month number to its name
    for month in activity_df.index:
        x_ticks_dict[month] = month_name[month-1]
    
    sports_fig.xaxis.ticker = FixedTicker(ticks=activity_df.index) # Show all the months as x-ticks
    sports_fig.xaxis.major_label_overrides = x_ticks_dict # Override the x-tick labels
    
    # Vertical bars
    # Set the bar height based on the chosen statistic and choose the data labels accordingly
    if statistic == 'Distance':
        height_choice = label_choice = 'Distance_km'
    elif statistic == 'Time':
        height_choice, label_choice = 'Time_h', 'time_spent'
    else:
        height_choice = label_choice = 'count'
        
    sports_fig.vbar(x='Month', top=height_choice, width=0.9, source=source, color='color')
    
    # Change the x_ticks to the names of the months
    x_ticks_dict = {}
    month_name = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for month in activity_df.index:
        x_ticks_dict[month] = month_name[month-1]

    sports_fig.xaxis.major_label_overrides = x_ticks_dict
        
    # Get the labels - it is necessary to have a "new" source without NaN values
    new_source=ColumnDataSource(activity_df.dropna())
    
    labels = LabelSet(x='Month', y=height_choice, text=label_choice, level='glyph', text_align='center',
                      source=new_source, render_mode='canvas', y_offset=3, text_font_size='10pt')
    
    # Add the labels to the figure
    sports_fig.add_layout(labels)

    # Show the figure
    st.bokeh_chart(sports_fig, True)