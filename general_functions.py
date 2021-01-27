import pandas as pd
import numpy as np

from bokeh.models import ColumnDataSource, LabelSet
from bokeh.plotting import figure

def create_color_time_spent_columns(activity_df, statistic):
    
    # Create a column with the colors of the bars. Green is the smallest, red the biggest and blue
    # are the others. Create also the time labels
    
    color, time_spent = [], [] # Variable to hold the colors and the time labels
    
    for idx in activity_df.index: # Loop over the index
        
        # Make sure the colors of the bars are set according to the statistic chosen
        if statistic == 'Distance':
            to_check = activity_df.Distance_km
        elif statistic == 'Time':
            to_check = activity_df.Time_h
        elif statistic == 'Counter':
            to_check = activity_df['count']
    
        # Add the color to the list
        if to_check[idx] == max(to_check):
            color.append('red')
        elif to_check[idx] == min(to_check):
            color.append('green')
        else:
            color.append('blue')
        
        # Create the time labels
        hour = int(activity_df.Time_h[idx]) # The integer part is the number of hours spent
        
        # By removing the integer part to the overall value, you get the minutes, which need to be multiplied
        # by 60 and then rounded to no decimal cases
        minutes = int(round((activity_df.Time_h[idx]-hour)*60, 0))
        
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

# =============================================================================

def title_label_plot(period, activity, statistic, activity_df, year=None):
    
    # Set the source as the curated dataframe
    source = ColumnDataSource(activity_df)
    
    # Set the right counter name when the mouse hovers over the bars
    if activity == 'Running':
        counter_name = 'Number of Runs'
    elif activity == 'Cycling':
        counter_name = 'Number of Bike Rides'
    else:
        counter_name = 'Number of Walks'
    
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
        
        if period == 'monthly':
            title = title+' '+'in'+' '+str(year) # Add the year in case it is monthly
    
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
        label = 'Kilometers'
        
        # In this case, yearly and monthly data have a different ending
        if period == 'yearly':
            title = 'Number of Kilometers '+verb+' per Year'
        
        elif period == 'monthly':
            title = 'Number of Kilometers '+verb+' per Month in '+str(year)
    
    else:
        label = counter_name
        
        # Make the distinction between yearly and monthly statistics
        if period == 'yearly':
            title = counter_name+' per Year'
        elif period == 'monthly':
            title = counter_name+' per Month in '+str(year)
    
    # Set the column for the x-axis label
    if period == 'yearly':
        x_axis = 'Year'
    elif period == 'monthly':
        x_axis = 'Month'
    
    # Instantiate the figure
    sports_fig = figure(title=title, x_axis_label=x_axis, y_axis_label = label, tooltips=tooltips,
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
    
    sports_fig.vbar(x=x_axis, top=height_choice, width=0.9, source=source, color='color')
    
    return sports_fig, height_choice, label_choice, source


