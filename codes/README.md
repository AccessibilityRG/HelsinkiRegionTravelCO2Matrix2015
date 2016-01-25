# Codes

__Helsinki Region Travel CO2 Matrix 2015__ is based on the same GIS analyses that were done when creating __[Helsinki Region Travel Time Matrix 2015](http://www.helsinki.fi/science/accessibility/data/helsinki-region-travel-time-matrix)__.
 
Producing the Helsinki Region Travel CO2 Matrix 2015 included following __analysis / processing steps__:
 
 1. Calculation of the Helsinki Region Travel Time Matrix 2015 ==> [More information here](https://github.com/AccessibilityRG/HelsinkiRegionTravelTimeMatrix2015)
 2. Calculation of the CO2 emissions for  
     1. Public Transportation (using specific [RouteCarbonCalculator.jar Java tool](CarbonCalculator/README.md)
     2. Private Car (using a function ___calculateCarCO2emissions()___ in __[funclib.py](funclib.py)__) 
 3. Pushing the data into PostGIS
 4. Calculating the fuel consumption for car in PostGIS
 5. Parsing the text file product from PostGIS
 
The analyses and processing phases support multiprocessing using Python [multiprocessing](https://docs.python.org/3.4/library/multiprocessing.html) module 
that makes possible to do processing in parallel utilizing multiple processors on a given machine. ==> Makes possible to do things faster. 
 
## Structure of the code

- __Analysis steps 1-3__ are run/controlled from __[TravelCO2_Matrix2015_calculator.py](TravelCO2_Matrix2015_calculator.py)__ file.
- __Analysis steps 4-5__ are run/controlled from __[CO2_Matrix2015_Parse_TextMatrix_from_PostGIS.py](CO2_Matrix2015_Parse_TextMatrix_from_PostGIS.py)__ file.

- __All the functions__ that are used can be found from __[funclib.py](funclib.py)__.
- __base.py__ has database connection details that __need to be modified before using the tools__!

