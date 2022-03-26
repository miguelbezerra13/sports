import streamlit as st

import numpy as np
import pandas as pd

from general_functions import define_counter_name

from bokeh.models import ColumnDataSource, FactorRange, Title
from bokeh.plotting import figure

def last_3_years_performance():
    
    # Page title
    st.markdown("<h1 style='text-align: center;'>Last 3 Years Evolution</h1>", unsafe_allow_html=True)
    
    # Load the dataframe
    df = pd.read_csv('rwc.csv', index_col=0, parse_dates=['Date'])
    
    col_1, col_2 = st.columns(2)
    
    # Variables to select the activity and the statistic
    activity = col_1.selectbox('Activity:', sorted(df.Type.unique()))
    statistic = col_2.selectbox('Statistic:', ('Count', 'Distance', 'Time'))
        
    ##############################################################################################
    # Data selection and curation
    ##############################################################################################
    
    # Limit the data you will consider based on the activity and the most recent 3 years, group it
    # by year and then by month, and sum it
    pre_activity_df = df.drop(['Hours', 'Minutes', 'Seconds'], axis=1).\
                      loc[((df.Type==activity) & (df.Year>max(df.Year)-3))].\
                      groupby(['Year', 'Month'])
    
    activity_df = pre_activity_df.sum()
    
    # Round the decimal cases of the distance to 2
    activity_df.Distance_km = activity_df.Distance_km.round(2)
    
    # Add the average speed column
    activity_df['avg_speed'] = pre_activity_df.mean()['AvgSpeed_km/h'].round(2)
    
    # Add the counts column
    activity_df['count'] = pre_activity_df.count()['Date']
    
    # Color and time labels columns
    color, time_spent = np.array([]), np.array([])
    years_to_consider = activity_df.index.levels[0]
    
    # Loop through the index, which has 2 keys, but consider only the year's part for the colors
    for year, month in activity_df.index:
        
        # Set one color to each year
        if year == min(years_to_consider):
            color = np.append(color, 'blue')
            
        elif year == max(years_to_consider):
            color = np.append(color, 'green')
        
        else:
            color = np.append(color, 'red')
            
        # Create the time labels
        hour = int(activity_df.Time_h[year, month]) # The integer part is the number of hours spent
        
        # By removing the integer part to the overall value, you get the minutes, which need to be
        # multiplied by 60 and then rounded to no decimal cases
        minutes = int(round((activity_df.Time_h[year, month]-hour)*60, 0)) 
        
        time = str(hour)+'h '+str(minutes)+'m' # Create the label
        time_spent = np.append(time_spent, time) # Add the label to the list

    # Add the columns to the dataframe
    activity_df['color'] = color
    activity_df['time_spent'] = time_spent
    
    # As there are some months in which some of the activities were not done and they should
    # "appear" in the graph, it is necessary to create rows for them
    # Variable to store the values for a row without any activity
    no_activity_row = [0, 0, 0, 0, 0, 0, 0, None, None]
    
    # Dataframe which will be used to create the plots
    df_to_plot = pd.DataFrame(columns=activity_df.columns)
    
    # Loop through the dataframe and consider only the years to check if they have all months
    for year in years_to_consider:
        
        # Restrict the dataframe to only one year at a time
        single_year_df = activity_df.loc[year]
        
        for month in range(1,13): # Loop over the months
            idx = str(year)+', '+str(month) # Create an index
            
            # If there were activities during the month, add the row of the activity_df
            if month in single_year_df.index:
                df_to_plot.loc[idx] = activity_df.loc[year, month]
            # Add the no activity row if there were any activities
            else:
                df_to_plot.loc[idx] = no_activity_row
    
    # List with the name of the months
    month_name = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    # List which will be on the x-axis
    x_axis = [(month, str(year)) for year in years_to_consider for month in month_name]
    
    # Add the list to the dataframe
    df_to_plot['x-axis'] = x_axis
    
    years = np.array([])
    for month in range(12*len(years_to_consider)):
        if month < 12:
            years = np.append(years, min(years_to_consider))
        elif month < 24:
            years = np.append(years, max(years_to_consider)-1)
        else:
            years = np.append(years, max(years_to_consider))
    
    df_to_plot['years'] = years
    
    #####################################################################################################
    # Plotting
    #####################################################################################################
    
    # Set the source as the curated dataframe
    source = ColumnDataSource(df_to_plot)
    
    counter_name = define_counter_name(activity)
    
    # Information when the mouse is hovered over the bars
    tooltips = [('Distance', "@Distance_km{0,0.00} km"), ('Time', "@time_spent"),
                ("Calories burned","@Calories{0,0}"),
                ("Cumulative Elevation Gain", "@ElevGain_m{0,0} m"),
                ("Average Speed", "@avg_speed{0.00} km/h"), (counter_name, "@count")]
    
    # Set the title and the y-axis label
    # The beginning and ending of the title will not change regardless of the activity
    title_beginning = 'Evolution of the '
    title_ending = 'During the Last 3 Years'
    if statistic == 'Time':
        title = title_beginning+'Time Spent '+activity
        label = 'Hours' # Y-axis label
    
    # If the chosen statistic is Distance
    elif statistic == 'Distance':
        if activity == 'Walking':
            verb = 'Walked'
        elif activity == 'Cycling':
            verb = 'Cycled'
        else:
            verb = 'Run'
        
        # As it happened for Time, the same procedure is applied to Distance
        title = title_beginning+'Number of Kilometers '+verb+' per Month'
        label = 'Kilometers'
    
    else:
        title = title_beginning+counter_name+' per Month'
        label = counter_name
    
    # Instantiate the figure
    evolution_fig = figure(y_axis_label=label, tooltips=tooltips,
                            plot_width=900, plot_height=500, tools='save',
                            x_range=FactorRange(*x_axis))
    
    # Add the ending of the title before so that it is below the other
    evolution_fig.add_layout(Title(text=title_ending, text_font_size='20px', align='center'),
                              'above')
    
    # Add the first line of the title
    evolution_fig.add_layout(Title(text=title, text_font_size='20px', align='center'), 'above')
    
    # Vertical bars
    # Set the bar height based on the chosen statistic and choose the data labels accordingly
    if statistic == 'Distance':
        height_choice = 'Distance_km'
    elif statistic == 'Time':
        height_choice = 'Time_h'
    else:
        height_choice = 'count'
    
    evolution_fig.vbar(x='x-axis', top=height_choice, width=0.9, color='color', source=source)
    
    # Remove unnecessary graph elements
    # Remove gridlines
    evolution_fig.xgrid.grid_line_color, evolution_fig.ygrid.grid_line_color = None, None

    # Remove x axis minor ticks
    evolution_fig.xaxis.minor_tick_line_color = None
    
    # Remove outline line
    evolution_fig.outline_line_color = None
    
    # Start of the y range
    evolution_fig.y_range.start = 0
    
    # Range padding of the x-axis
    evolution_fig.x_range.range_padding = 0.1
    
    # Rotate the labels of the years
    evolution_fig.xaxis.major_label_orientation = 1
    
    # Show the figure
    st.bokeh_chart(evolution_fig, True)