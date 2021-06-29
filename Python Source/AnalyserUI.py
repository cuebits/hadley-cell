import pymannkendall
import pandas
import geopandas
import smoomapy
import os
import matplotlib.pyplot as plt
import matplotlib

from shapely.geometry import Point
from numpy import reshape, linspace
from datetime import datetime

def main():

    # Initialise variables and set working directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)) + "\..")
    output_dir = os.getcwd() + "\outputs\\"

    print(os.getcwd())

    try:
        mk_significance_alpha = float(input("Enter significance alpha (default = 0.05): "))
    except ValueError:
        mk_significance_alpha = 0.05

    input_file = input("Enter input CSV file name, excluding .csv extension (default name is 'data'): ") or "data"
    
    if input("Does file have coordinates? (Default yes. Type no or n for no.): ").upper() in ["N", "NO"]:
        coords_in_file = False
    else:
        coords_in_file = True
    
    # Set file names and output files
    file_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_dir += file_time + "\\"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Read CSV file into a pandas data frame 
    data_frame = pandas.read_csv(input_file + ".csv", sep=",")

    # Extract the dates column and place it in a series
    dates = pandas.Series(data_frame["Date"])

    # If input file has latitude and longitude rows, remove from date column
    if coords_in_file:
        dates = dates.drop(index = [0, 1])
    
    # Convert to a time series
    dates = pandas.to_datetime(dates)

    # Create new data frames for Sen's Slopes, M-K Tests, and Coordinates
    sens_dataframe = pandas.DataFrame()
    mk_dataframe = pandas.DataFrame()
    if coords_in_file:
        coor_dataframe = pandas.DataFrame()

    # Iterate for each station in the data frame
    for label, content in data_frame.iteritems():
        
        # Skip the dates column
        if label == "Date":
            continue

        # If input file has lat/lon rows, extract the two rows
        if coords_in_file:
            coor_dataframe[label] = [content.iloc[0], content.iloc[1]]
            content = content.drop(index = [0, 1])

        # Convert the column to a time series
        content = pandas.Series(content.values, index = dates)

        # Reshape the time series into a matrix with months as columns
        monthly_array = content.values                              # Create an array with the values from the current data frame column
        monthly_array = reshape(monthly_array, (-1, 12)).T    # Reshape to 12 x N, then transpose so each array index corresponds with a month

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
    sens_dataframe["Month"] = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    sens_dataframe = sens_dataframe.set_index("Month")

    mk_dataframe["Month"] = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    mk_dataframe = mk_dataframe.set_index("Month")

    if coords_in_file:
        coor_dataframe["Coordinate"] = ["Latitude", "Longitude"]
        coor_dataframe = coor_dataframe.set_index("Coordinate")

    
    ######## Output data analysis files
    sens_dataframe.T.to_csv(output_dir + "sens_" + file_time + ".csv")
    mk_dataframe.T.to_csv(output_dir + "mk_" + file_time + ".csv")
    #coor_dataframe.T.to_csv(output_dir + "coordinates_" + file_time + ".csv") [No need for this one at the moment]
    
    if not coords_in_file:
        input("Analysis CSV files generated in output folder. No coordinates in file to generate map plots.")
        os.system("pause")
        return 101

    ######## Output station location plot
    # Temp set extents of map. [TAKE INPUT LATER]
    axis_buffer = 5
    minx, miny, maxx, maxy = min(coor_dataframe.loc["Longitude", :]) - axis_buffer, min(coor_dataframe.loc["Latitude", :]) - axis_buffer, max(coor_dataframe.loc["Longitude", :]) + axis_buffer, max(coor_dataframe.loc["Latitude", :]) + axis_buffer

    # Temp extents
    # minx, miny, maxx, maxy = -130, 22.5, -65, 55

    # Axes subplots
    ax = plt.subplot()
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_facecolor("#d1e0e6")

    world = geopandas.read_file("GISData\\ne_10m_admin_0_countries.shp") # geopandas.datasets.get_path('naturalearth_lowres')
    us_states = geopandas.read_file("GISData\\cb_2018_us_state_500k.shp")
    mask = us_states[(us_states.NAME!="Alaska")]

    world.to_csv("output.csv")

    country = input("Enter country of analysis: ")

    mask = world[(world.SOVEREIGNT==country)]

    water = geopandas.read_file("GISData\\World_Lakes.shp")

    gdf = df_to_gfd(coor_dataframe, coor_dataframe, 4326)

    gdf.plot(ax=ax, color="k", markersize=3, zorder=100)
    us_states.plot(ax=ax, color="#f5f1e9", zorder=2)
    water.plot(ax=ax, color="#d1e0e6", zorder=3)
    world.plot(ax=ax, color="#c6cccf", zorder=1)

    plt.title(label="RAINFALL STATION LOCATIONS")
    plt.savefig(output_dir + "stat_loc_" + file_time + ".png", dpi=600)

    ####### Work out IDW maps

    # Prepare GeoDataFrame for Sen's Slopes
    sens_gdf = sens_dataframe.T.copy()
    sens_gdf["Latitude"] = coor_dataframe.loc["Latitude", :]
    sens_gdf["Longitude"] = coor_dataframe.loc["Longitude", :]
    sens_gdf = geopandas.GeoDataFrame(sens_gdf, geometry=geopandas.points_from_xy(sens_gdf.Longitude, sens_gdf.Latitude))

    # Define precision of IDW contours
    num_breaks = 200
    breaks_min = -4 #round((min(sens_dataframe.min())), ndigits=3)
    breaks_max = 4 #round((max(sens_dataframe.max())), ndigits=3)
    plot_breaks = linspace(breaks_min, breaks_max, num_breaks)    

    i = 1 # For file naming, keeps months in chronological order, not alphabetical 
    for month, slopes in sens_gdf.iteritems():
        
        # Skip non-month columns
        if month == "Latitude" or month == "Longitude" or month == "geometry":
            continue
        
        # Create new geodataframe for each month
        month_gdf = geopandas.GeoDataFrame(slopes, geometry=geopandas.points_from_xy(sens_gdf.Longitude, sens_gdf.Latitude))
        
        # Perform IDW functions
        idw = smoomapy.SmoothIdw(month_gdf, month, 1, nb_pts=20000, mask=mask)
        res = idw.render(nb_class=num_breaks, user_defined_breaks=plot_breaks, disc_func="equal_interval", output="GeoDataFrame")

        #divider = make_axes_locatable(ax)
        #cax = divider.append_axes("right", size="5%", pad=0.1)

        # Reset figure
        plt.figure()
        fig, ax = plt.subplots()

        ax.set_xlim(minx, maxx)
        ax.set_ylim(miny, maxy)
        ax.set_facecolor("#d1e0e6")

        gdf.plot(ax=ax, color="k", markersize=3, zorder=100, alpha=0.2)
        us_states.plot(ax=ax, color="#f5f1e9", zorder=2)
        water.plot(ax=ax, color="#d1e0e6", zorder=3)
        world.plot(ax=ax, color="#c6cccf", zorder=1)

        res.plot(ax=ax, cmap="RdBu", column="center", linewidth=0.1, zorder=99, legend=False)

        # Create normalised colour bar
        norm = matplotlib.colors.TwoSlopeNorm(vmin=breaks_min, vcenter=0, vmax=breaks_max)
        cbar = plt.cm.ScalarMappable(norm=norm, cmap="RdBu")
        fig.colorbar(cbar, ax=ax)

        plt.title(label=month + " Sens's Slopes")
        plt.savefig(output_dir + str(i) + "_" + month + "_sens_" + file_time + ".png", dpi=600)
        plt.close()

        i += 1

    os.system("pause")


# Function for the tests to be conducted over each data series
def run_tests(data, alpha):

    slope_test = pymannkendall.sens_slope(data)
    mk_test = pymannkendall.original_test(data, alpha=alpha)

    return slope_test, mk_test


# Convert dataframe with latitude and longitude columns to GeoDataFrame
def df_to_gfd(inputdf, coor_df, crs):
    df = inputdf.T
    coor_df = coor_df.T
    geometry = [Point(xy) for xy in zip(coor_df.loc[:, "Longitude"], coor_df.loc[:, "Latitude"])]
    return geopandas.GeoDataFrame(df, geometry=geometry, crs=crs)


main()