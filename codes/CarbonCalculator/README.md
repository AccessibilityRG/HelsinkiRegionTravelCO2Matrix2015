# Route Carbon Calculator 2015

__Route Carbon Calculator 2015__ is a Java app that parses travel distances and calculates CO2 emissions for Public Transportation (PT) modes. 
Input data that the tool uses is a result file of __[MetropAccess-Reititin](http://blogs.helsinki.fi/accessibility/reititin/)__ tool that calculates travel times and distances based on public transportation
schedules and Open Street Map road network. MetropAccess-Reititin also parses detailed information about individual trip legs that were taken during the route, 
including e.g. information about the distance that was travelled with specific transport mode on a route (e.g. bus, tram, metro, walking etc.).
Route Carbon Calculator 2015 takes advantages of this information and calculates the CO2 emissions based on specific Carbon Emission Factors ([more info here](http://www.hsljalki.fi/en/menu/info)) 
and on the distances that were travelled with PT vehicles. 

## Running the Route Carbon Calculator Java app

For running the tool you need to have Java JDK (Java Development Kit) installed. Download it from [here](http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html).

Use the following command in command prompt to calculate the CO2 emissions for different Public Transportation modes: 

    java -jar RouteCarbonCalculator.jar inputfile.txt outputfile.txt errorfile.txt
    
For example:

    java -jar RouteCarbonCalculator2015.jar C:\...\1_Massa-ajo_2015_Joukkoliikenne_Rushhour.txt C:\...\1_Massa-ajo_2015_Joukkoliikenne_Rushhour_CO2.txt C:\...\1_Massa-ajo_2015_Joukkoliikenne_Rushhour_CO2_ERRORS.txt
    
## Source codes

 - [RouteCarbonCalculator.java](RouteCarbonCalculator.java) is a class that calculates the CO2 emissions by parsing the travel distances of each transport mode and multiplying it with corresponding carbon emission factor.
    - Static variables *busCO2*, *tramCO2*, *trainCO2*, *metroCO2*, *ferryCO2* can be used to pass the CO2 emissions for each travel mode separately   
 - [RouteCarbonCalculatorApp.java](RouteCarbonCalculatorApp.java) is a class that handles the input parameters etc. (entry point for the tool)
 - __RouteCarbonCalculator.jar__ is a built version of the Java tool  