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
