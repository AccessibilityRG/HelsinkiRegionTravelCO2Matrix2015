# Codes

__Helsinki Region Travel CO2 Matrix 2015__ is based on the same GIS analyses that were done when creating __[Helsinki Region Travel Time Matrix 2015](http://www.helsinki.fi/science/accessibility/data/helsinki-region-travel-time-matrix)__.
 
Producing the Helsinki Region Travel CO2 Matrix 2015 included following analysis / processing steps:
 
 1. Calculation of the Helsinki Region Travel Time Matrix 2015 ==> [More information here](https://github.com/AccessibilityRG/HelsinkiRegionTravelTimeMatrix2015)
 2. Calculation of the CO2 emissions for  
     1. Public Transportation (using specific [RouteCarbonCalculator.jar Java tool](CarbonCalculator/README.md)
     2. Private Car (using function ___calculateCarCO2emissions()___ in __[funclib.py](funclib.py)__) 
 3. Pushing the data into PostGIS
 4. Calculating the fuel consumption for car in PostGIS
 5. Parsing the text file product from PostGIS

Analysis steps 1-3 are run/controlled from __[TravelCO2_Matrix2015_calculator.py](TravelCO2_Matrix2015_calculator.py)__ file.
Analysis steps 4-5 are run/controlled from __[CO2_Matrix2015_Parse_TextMatrix_from_PostGIS.py](CO2_Matrix2015_Parse_TextMatrix_from_PostGIS.py)__ file.

All the main functions that are used can be found from __[funclib.py](funclib.py)__.
