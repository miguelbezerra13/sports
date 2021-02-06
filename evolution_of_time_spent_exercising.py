import pandas as pd
import numpy as np
import streamlit as st

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.models.tickers import FixedTicker
from bokeh.models.tools import HoverTool

def evolution_of_time_spent_exercising():
    
    # Page title
    st.markdown("<h1 style='text-align: center;'>Evolution of the Time Spent Exercising</h1>",
                unsafe_allow_html=True)
    
    # Select the magnitude
    magnitude = st.selectbox('Magnitude:', ('Absolute', 'Relative'))
    
    # Load the dataframe
    df = pd.read_csv('rwc.csv', index_col=0, parse_dates=['Date'])
    
    # Drop the unnecessary columns for the analysis and group the data by Activity and then by Year
    pre_activity_df = df.drop(['Hours', 'Minutes', 'Seconds', 'Month'], axis=1).\
                 groupby(['Type', 'Year'])
    
    activity_df = pre_activity_df.sum()
    
    # Round the decimal cases of the distance to 2
    activity_df.Distance_km = activity_df.Distance_km.round(2)
    
    # Add the average speed column
    activity_df['avg_speed'] = pre_activity_df.mean()['AvgSpeed_km/h'].round(2)
    
    # Add the counts column
    activity_df['count'] = pre_activity_df.count()['Date']
    
    # Add the time labels
    time_spent = np.array([])  # Time labels column
    for year, activity in activity_df.index: # Loop through the index, which has 2 keys
            
        # Create the time labels
        hour = int(activity_df.Time_h[year, activity]) # The integer part is the number of hours spent
        
        # By removing the integer part to the overall value, you get the minutes, which need to be
        # multiplied by 60 and then rounded to no decimal cases
        minutes = int(round((activity_df.Time_h[year, activity]-hour)*60, 0)) 
        
        time = str(hour)+'h '+str(minutes)+'m' # Create the label
        time_spent = np.append(time_spent, time) # Add the label to the list
    
    activity_df['time_spent'] = time_spent # Add the column
    
    df_to_plot_dict = {} # Create a dictionary from which the dataframe will be created
    
    # It is necessary to loop over everything in the activity_df (each key from the index and columns)
    # The keys of the df_to_plot_dict will be the column names which will be composed of the previous
    # name of the column plus a suffix of "_<activity name>". If the key has no associated value, a 
    # list with the first element will be added. From that point on, the values will just be appended.
    for activity in activity_df.index.levels[0]: # Loop over the activities
        for col in activity_df.columns: # Loop over the columns
            for year in activity_df.index.levels[1]:
                if col+'_'+activity not in df_to_plot_dict.keys():
                    df_to_plot_dict[col+'_'+activity] = [activity_df[col][activity, year]]
                else:
                    df_to_plot_dict[col+'_'+activity].append(activity_df[col][activity, year])
    
    df_to_plot = pd.DataFrame.from_dict(df_to_plot_dict) # Create the dataframe from the dictionary
    
    df_to_plot['year'] = activity_df.index.levels[1] # Add the year to the dataframe
    
    # Create columns with the share of the amount of time spent in the activities
    # Create the variables to store the share values
    share_Cycling, share_Running, share_Walking = np.array([]), np.array([]), np.array([])
    
    for idx in df_to_plot.index: # Loop through the index of the df_to_plot
        
        # Select the columns of the time
        time_h_cols = df_to_plot.loc[:, df_to_plot.columns.str.startswith('Time_h_')].columns
        
        # Sum all the time spent in the activities in the year under consideration
        all_time = df_to_plot[time_h_cols].loc[idx].sum()
        
        # Add the share of the time spent to the array
        share_Cycling = np.append(share_Cycling, ((df_to_plot['Time_h_Cycling'][idx]/all_time)*100))
        share_Running = np.append(share_Running, ((df_to_plot['Time_h_Running'][idx]/all_time)*100))
        share_Walking = np.append(share_Walking, ((df_to_plot['Time_h_Walking'][idx]/all_time)*100))
    
    # Add the arrays to the dataframe
    df_to_plot['share_Cycling'] = share_Cycling
    df_to_plot['share_Running'] = share_Running
    df_to_plot['share_Walking'] = share_Walking
    
    # Change the name of the columns to be rendered based on the chosen magnitude
    if magnitude == 'Absolute':
        selection = 'Time_h_'
    elif magnitude == 'Relative':
        selection = 'share_'
        
    # Identify the columns whose name should be changed and store them in a list
    to_replace = df_to_plot.loc[:, df_to_plot.columns.str.startswith(selection)].columns
    
    # Dictionary to be used to rename the columns
    new_names = {col:col[len(selection):] for col in to_replace}
    df_to_plot = df_to_plot.rename(columns=new_names) # Rename the columns
    
    colors = ['blue', 'red', 'green'] # List for the colors of the segments
    
    activities = list(activity_df.index.levels[0]) # List for the legend
    
    if magnitude == 'Absolute':
        
        # Create a column for the total amount of time
        total_time_y = [round(sum(df_to_plot[activities].loc[idx]),2) for idx in df_to_plot.index]
        df_to_plot['total_time_y'] = total_time_y # Add to the dataframe
        
        # Create a column for the labels of the total amount of time
        total_time_label = np.array([])
        for t in total_time_y:
            hours = str(int(t)) # Get the total amount of hours
            minutes = int((t-int(t))*60) # Remove the hours to get the minutes left
            
            # Format the minutes to either not show or to have a 0 if there's only one digit
            if minutes == 0: 
                minutes = ''
            elif minutes < 10:
                minutes = '0'+str(minutes)
            else:
                minutes = str(minutes)
            
            total_time_label = np.append(total_time_label, hours+':'+minutes+"'")
        
        df_to_plot['total_time_label'] = total_time_label
    
    #####################################################################################################
    # Plotting
    #####################################################################################################
    
    # Set the source as the curated dataframe
    source = ColumnDataSource(df_to_plot)
    
    # Title and y-axis label adaptation
    if magnitude == 'Absolute':
        title = "Evolution of the Time Spent per Activity per Year"
        y_axis_label = 'Hours'
        
    else:
        title = "Evolution of the Share of Time Spent per Activity per Year"
        y_axis_label = 'Percentage of Time Spent'
    
    # Instantiate the figure
    evo_fig = figure(plot_width=900, plot_height=500, title=title, tools="save",
                     y_axis_label=y_axis_label, x_axis_label='Year',
                     x_range=(min(df_to_plot.year)-0.5, max(df_to_plot.year)+1.5))
        
    # Assign a variable to the stacked vertical bars to customize the hovertools
    renderers = evo_fig.vbar_stack(activity_df.index.levels[0], x='year', width=0.9, color=colors,
                                   source=source, line_color='black', legend_label=activities)
    
    for glyph in renderers: # Loop over the glyphs (which are the layers of the bar)
        activity = glyph.name # Assign the activity name to a variable
        
        # Select only the columns associated with the activity under consideration
        act_df = df_to_plot.loc[:, df_to_plot.columns.str.endswith(activity)]
        
        # Create a list with the column names with @ before the name so that it can be added to
        # the tooltips
        act_df_cols = ['@'+col for col in act_df.columns]
        # Define the tooltips with the respective formats
        hover = HoverTool(tooltips=[('Distance', act_df_cols[0]+"{0,0.00} km"),
                                    ('Time', act_df_cols[7]),
                                    ("Calories Burned", act_df_cols[2]+"{0,0}"),
                                    ("Cumulative Elevation Gain", act_df_cols[3]+"{0,0} m"),
                                    ("Average Speed", act_df_cols[5]+"{0.00} km/h"),
                                    ("Number of Activities", act_df_cols[6]),
                                    ('Percentage of Time Spent', act_df_cols[8]+"{0.00}%")],
                          renderers=[glyph])
        
        evo_fig.add_tools(hover) # Add the customized hovertool to the figure
    
    # Tweak the title
    evo_fig.title.align = 'center'
    evo_fig.title.text_font_size = "20px"

    if magnitude == 'Absolute':
        labels = LabelSet(x='year', y='total_time_y', text='total_time_label', level='glyph',
                          text_align='center', source=source, render_mode='canvas', y_offset=3)
    
        # Add the labels to the figure
        evo_fig.add_layout(labels)    

    # Remove the gridlines
    evo_fig.xgrid.grid_line_color, evo_fig.ygrid.grid_line_color = None, None

    evo_fig.outline_line_color = None # Remove the outline
    
    evo_fig.legend.location = 'center_right' # Define the location of the legend
    
    evo_fig.y_range.start = 0 # Start of the y range
    
    evo_fig.xaxis.minor_tick_line_color = None  # Turn off x-axis minor ticks
    
    # Customize the x-ticks
    evo_fig.xaxis.ticker = FixedTicker(ticks=df_to_plot.year)
    
    # Show the figure
    st.bokeh_chart(evo_fig, True)