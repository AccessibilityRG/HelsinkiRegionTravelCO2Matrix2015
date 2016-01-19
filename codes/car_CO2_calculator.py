import geopandas as gpd
import pandas as pd
import os, sys

"""
   This calculator calculates the CO2 emissions from Car in Helsinki Region.
   CO2 emission per kilometer is 171 grams that is used by Helsinki Region Transport (HRT).
   More info here: http://www.hsljalki.fi/fi/menu/info
"""
def calculateCarCO2emissions(src_file, output_dir, car_co2_emission=171):
    # Read data into GeoDataFrame
    print("Reading: %s" % os.path.basename(src_file))
    data = gpd.read_file(src_file)

    # Calculate CO2 distance (in meters) and total CO2 emissions (in grams per kilometer) from car usage
    print("Calculating the driven distance and CO2 emissions")
    data['distDriven'] = data['Pituus_Ajo'] + data['Pituus_P_E']
    data['co2FromCar'] = (data['distDriven'] / 1000.0) * car_co2_emission

    # Select columns
    slct_cols = ['from_id', 'to_id', 'Pituus_TOT', 'distDriven', 'co2FromCar']
    outdata = data[slct_cols]

    # Create output file
    outname = "%s_CO2_emissions.txt" % os.path.basename(src_file).split('.')[0]
    outfp = os.path.join(output_dir, outname)

    # Save CO2 data to disk
    print("Saving the CO2 emissions to: %s" % outfp)
    outdata.to_csv(outfp, sep=';', index=False)

    # Return the output path
    return outfp
