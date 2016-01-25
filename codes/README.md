# Codes

__Helsinki Region Travel CO2 Matrix 2015__ is based on the same GIS analyses that were done when creating __[Helsinki Region Travel Time Matrix 2015](http://www.helsinki.fi/science/accessibility/data/helsinki-region-travel-time-matrix)__.
 
Producing the Helsinki Region Travel CO2 Matrix 2015 included following analysis / processing steps:
 
 1. Calculation of the Helsinki Region Travel Time Matrix 2015 ==> [More information here](https://github.com/AccessibilityRG/HelsinkiRegionTravelTimeMatrix2015)
 2. Calculation of the CO2 emissions for:
   2.1 Public Transportation (using specific [RouteCarbonCalculator.jar Java tool]()
   2.2 Private Car
 3. Pushing the data into PostGIS
 4. Calculating the fuel consumption for car in PostGIS
 5. Parsing the text file product from PostGIS

## Run Route Carbon Calculator Java app

For running the tool you need to have Java JDK (Java Development Kit) installed. Download it from [here](http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html).

Use the following command in command prompt: 

    java -jar RouteCarbonCalculator.jar + inputfile outputfile errorfile
    
For example:

    java -jar RouteCarbonCalculator2015.jar E:\Matriisiajot2015\RESULTS\MassaAjot2015_PT_klo08_FixedKalkati\Joukkoliikenne\1_Massa-ajo_2015_Joukkoliikenne_Rushhour.txt E:\Matriisiajot2015\RESULTS\MassaAjot2015_PT_klo08_CARBON\RESULTS\1_Massa-ajo_2015_Joukkoliikenne_Rushhour_CO2.txt E:\Matriisiajot2015\RESULTS\MassaAjot2015_PT_klo08_CARBON\ERRORS\1_Massa-ajo_2015_Joukkoliikenne_Rushhour_CO2_ERRORS.txt
     

