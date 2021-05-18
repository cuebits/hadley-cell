import pymannkendall
import numpy
import pandas
import geopandas
import smoomapy
import json
import datetime
import os

from shapely.geometry import Point

mk_significance_alpha = 0.1
output_dir = os.getcwd() + "\outputs\\"

def main():

    # Read CSV file into a pandas data frame 
    data_frame = pandas.read_csv("US_Data.csv", sep=",")

    # Extract the dates column and place it in a series
    dates = pandas.Series(data_frame["Date"])

    # If input file has latitude and longitude rows, remove from date column
    if True:
        dates = dates.drop(index = [0, 1])
    
    # Convert to a time series
    dates = pandas.to_datetime(dates)

    # Create new data frames for Sen's Slopes, M-K Tests, and Coordinates
    sens_dataframe = pandas.DataFrame()
    mk_dataframe = pandas.DataFrame()
    coor_dataframe = pandas.DataFrame()

    # Iterate for each station in the data frame
    for label, content in data_frame.iteritems():
        
        # Skip the dates column
        if label == "Date":
            continue

        # If input file has lat/lon rows, drop the two rows
        if True:
            coor_dataframe[label] = [content.iloc[0], content.iloc[1]]
            content = content.drop(index = [0, 1])

        # Convert the column to a time series
        content = pandas.Series(content.values, index = dates)

        # Reshape the time series into a matrix with months as columns
        monthly_array = content.values                              # Create an array with the values from the current data frame column
        monthly_array = numpy.reshape(monthly_array, (-1, 12)).T    # Reshape to 12 x N, then transpose so each array index corresponds with a month

        # Create temporary columns for storing into the new data frame
        sens_temp = []
        mk_temp = []

        # For each column in the array, run the tests
        for month in monthly_array:
            
            # Append the desired test results to the sens_temporary column
            sens_result, mk_result = run_tests(month, mk_significance_alpha)
            sens_temp.append(sens_result.slope)
            mk_temp.append(mk_result.trend)

        # Add each station to the data frames
        sens_dataframe[label] = sens_temp
        mk_dataframe[label] = mk_temp

    # Set data frame indexes
    sens_dataframe["Month"] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    sens_dataframe = sens_dataframe.set_index("Month")

    mk_dataframe["Month"] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    mk_dataframe = mk_dataframe.set_index("Month")

    coor_dataframe["Coordinate"] = ["Latitude", "Longitude"]
    coor_dataframe = coor_dataframe.set_index("Coordinate")

    # Set file names and output files

    file_time = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    sens_dataframe.T.to_csv(output_dir + "sens_" + file_time + ".csv")
    mk_dataframe.T.to_csv(output_dir + "mk_" + file_time + ".csv")
    coor_dataframe.T.to_csv(output_dir + "coordinates_" + file_time + ".csv")
    

# Function for the tests to be conducted over each data series
def run_tests(data, alpha):

    slope_test = pymannkendall.sens_slope(data)
    mk_test = pymannkendall.original_test(data, alpha=alpha)

    return slope_test, mk_test


main()

