from pandas._libs.tslibs import Timestamp
import pymannkendall
import numpy
import sys
import csv
import pandas
import datetime

def main():

    # Read CSV file into a pandas data frame 
    data_frame = pandas.read_csv("US_Data.csv", sep=",")
    print(data_frame)

    # Extract the dates column and place it in a series
    dates = pandas.Series(data_frame["Date"])

    # If input file has latitude and longitude rows, remove from date column
    if True:
        dates = dates.drop(index = [0, 1])
    
    # Convert to a time series
    dates = pandas.to_datetime(dates)

    # Create a new data frame for Sen's Slope values
    sens_dataframe = pandas.DataFrame()

    # Iterate for each station in the data frame
    for label, content in data_frame.iteritems():
        
        # If input file has lat/lon rows, drop the two rows
        if True:
            content = content.drop(index = [0, 1])

        # Skip the dates column
        if label == "Date":
            continue

        # Convert the column to a time series
        content = pandas.Series(content.values, index = dates)

        # Reshape the time series into a matrix with months as columns
        monthly_array = content.values                              # Create an array with the values from the current data frame column
        monthly_array = numpy.reshape(monthly_array, (-1, 12)).T    # Reshape to 12 x N, then transpose so each array index corresponds with a month

        # Create a temporary column for storing into the new data frame
        temp = []

        # For each column in the array, run the tests
        for month in monthly_array:
            
            # Append the desired test results to the temporary column
            result = run_tests(month)
            temp.append(result.slope)

        print(label)
        print(temp)

        # Add each station to the data frame
        sens_dataframe[label] = temp

    sens_dataframe["Month"] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    sens_dataframe = sens_dataframe.set_index("Month")

    print(sens_dataframe)

    sens_dataframe.to_csv("output.csv")


# Function for the tests to be conducted over each data series
def run_tests(data):

    slope_test = pymannkendall.sens_slope(data)

    return slope_test



main()

