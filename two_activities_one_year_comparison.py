import streamlit as st

import numpy as np
import pandas as pd

from bokeh.models import ColumnDataSource, FactorRange, Title
from bokeh.plotting import figure

def two_activities_one_year_comparison():
    
    # Page title
    st.markdown("<h1 style='text-align: center;'>Two Activities One Year Comparison Comparison</h1>", unsafe_allow_html=True)
    
    # Load the dataframe
    df = pd.read_csv('rwc.csv', index_col=0, parse_dates=['Date'])
    
    # Variables declared but the logic is missing
    col_1, col_2, col_3, col_4 = st.columns(4)
    
    # Variables to select the activity and the statistic
    year_options=df.Year.unique()
    year = col_1.slider('Year:', int(min(year_options)), int(max(year_options)), step=1)
    statistic = col_2.selectbox('Statistic:', ('Count', 'Distance', 'Time'))
    
    # Restrict the set of available years based on the chosen activity
    activity_1_options = df.loc[df.Year==year].Type.unique()
    activity_1 = col_3.selectbox('Base activity: (green)', activity_1_options)
    
    activity_2_options = np.delete(activity_1_options, np.where(activity_1_options == activity_1))
    activity_2 = col_4.selectbox('Comparison activity: (red)', activity_2_options)
        
    ##############################################################################################
    # Data selection and curation
    ##############################################################################################
    
    # Limit the data you will consider based on the chosen year and the activities, group it by activities and
    # then by month, and sum it. Even though there are only 3 activies, it is better to select them
    # directly, rather than by selecting based on the negation of the remaining as more activities could
    # be added in the future
    pre_activity_df = df.loc[((df.Year==year) & ((df.Type==activity_1) | (df.Type==activity_2)))].\
                      groupby(['Type', 'Month'])
    
    activity_df = pre_activity_df.sum().drop('Year', axis=1)
    
    # Round the decimal cases of the distance to 2
    activity_df.Distance_km = activity_df.Distance_km.round(2)
    
    # Add the average speed column
    activity_df['avg_speed'] = pre_activity_df.mean()['AvgSpeed_km/h'].round(2)
    
    # Add the counts column
    activity_df['count'] = pre_activity_df.count()['Date']
    
    # Color (same color code as used in yearly_comparison.py) and time labels columns
    color = ['green' if act == activity_1 else 'red' for act, month in activity_df.index] # Color column
    
    time_spent = np.array([])  # Time labels column
    for year, month in activity_df.index: # Loop through the index, which has 2 keys
            
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
    no_activity_row = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, None, None]
    
    # Dataframe which will be used to create the plots
    df_to_plot = pd.DataFrame(columns=activity_df.columns)
    
    # Loop through the dataframe and consider only the highest level of the grouping to check if they
    # have all months
    for act in activity_df.index.levels[0]:
        
        # Restrict the dataframe to only one activity
        single_activity_df = activity_df.loc[act]
        
        for month in range(1,13): # Loop over the months
            idx = str(act)+', '+str(month) # Create an index
            
            # If there were activities during the month, add the row of the activity_df
            if month in single_activity_df.index:
                df_to_plot.loc[idx] = activity_df.loc[act, month]
            # Add the no activity row if there were any activities
            else:
                df_to_plot.loc[idx] = no_activity_row
        
    # List with the name of the months
    month_name = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    # List which will be on the x-axis
    x_axis = [(month, act) for act in activity_df.index.levels[0] for month in month_name]
    
    # Add the list to the dataframe
    df_to_plot['x-axis'] = x_axis
    
    #####################################################################################################
    # Plotting
    #####################################################################################################
    
    # Set the source as the curated dataframe
    source = ColumnDataSource(df_to_plot)
    
    # Information when the mouse is hovered over the bars
    tooltips = [('Distance', "@Distance_km{0,0.00} km"), ('Time', "@time_spent"),
                ("Calories burned","@Calories{0,0}"),
                ("Cumulative Elevation Gain", "@ElevGain_m{0,0} m"),
                ("Average Speed", "@avg_speed{0.00} km/h"), ("Number of activities", "@count")]
    
    # Set the title and the y-axis label
    # The beginning and ending of the title will not change regardless of the activity
    title_beginning = 'Comparison of the '
    title_ending = ' between '+activity_1+' and '+activity_2
    if statistic == 'Time':
        title = title_beginning+'Time Spent in '+str(year)
        label = 'Hours' # Y-axis label
    
    # If the chosen statistic is Distance
    elif statistic == 'Distance':
        # As it happened for Time, the same procedure is applied to Distance
        title = title_beginning+'Distance Covered in '+str(year)+' per Month'
        label = 'Kilometers'
    
    else:
        title = title_beginning+'Number of Activities in '+str(year)+' per Month'
        label = 'Number of Activities'
    
    # Instantiate the figure
    comparison_fig = figure(y_axis_label=label, tooltips=tooltips,
                            plot_width=900, plot_height=500, tools='save',
                            x_range=FactorRange(*x_axis))
    
    # Add the ending of the title before so that it is below the other
    comparison_fig.add_layout(Title(text=title_ending, text_font_size='20px', align='center'),
                              'above')
    
    # Add the first line of the title
    comparison_fig.add_layout(Title(text=title, text_font_size='20px', align='center'), 'above')
    
    # Vertical bars
    # Set the bar height based on the chosen statistic and choose the data labels accordingly
    if statistic == 'Distance':
        height_choice = 'Distance_km'
    elif statistic == 'Time':
        height_choice = 'Time_h'
    else:
        height_choice = 'count'
    
    comparison_fig.vbar(x='x-axis', top=height_choice, width=0.9, color='color', source=source)
    
    # Remove unnecessary graph elements
    # Remove gridlines
    comparison_fig.xgrid.grid_line_color, comparison_fig.ygrid.grid_line_color = None, None

    # Remove x axis minor ticks
    comparison_fig.xaxis.minor_tick_line_color = None
    
    # Remove outline line
    comparison_fig.outline_line_color = None
    
    # Start of the y range
    comparison_fig.y_range.start = 0
    
    # Range padding of the x-axis
    comparison_fig.x_range.range_padding = 0.1
    
    # Rotate the labels of the years
    comparison_fig.xaxis.major_label_orientation = 1

    # Show the figure
    st.bokeh_chart(comparison_fig, use_container_width=True)