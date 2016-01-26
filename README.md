# Helsinki Region Travel CO2 Matrix 2015

This repository demonstrates / documents how [Helsinki Region Travel CO2 Matrix 2015](http://www.helsinki.fi/science/accessibility/data) is calculated. 
Dataset was produced by [Accessibility Research Group](http://www.helsinki.fi/science/accessibilty), University of Helsinki.

__Contents:__

- [What is Helsinki Region Travel CO2 Matrix 2015?](#what-is)
- [Attributes of Helsinki Region Travel CO2 Matrix 2015](#attributes)
- [How calculations were done?](#calculations)
   - [CO2 calculations](#co2-calculations)
   - [Fuel consumption calculations](#fc-calculations)
- [Licence](#license)
- [How to cite this work?](#how-to-cite)
- [Codes](#codes)
- [Contribution / Contact](#contact)

(P.S. You can read Finnish description from [Metadata](metadata/METADATA_Helsinki-Region-Travel-CO2-Matrix-2015.txt).)

## <a name="what-is"></a>What is Helsinki Region Travel CO2 Matrix 2015?
 
[__Helsinki Region Travel CO2 Matrix 2015__](http://www.helsinki.fi/science/accessibility/data) is a dataset that contains CO2 emissions (+some additional attributes) produced by public transportation (PT) and private car
for routes between all 250 m x 250 m grid cell centroids (n = 13231) in the Capital Region of Helsinki ([see this map](http://www.helsinki.fi/science/accessibility/tools/YKR/YKR_Identifier.html)). Calculations were done separately for two different time of the day using 
rush hour (08:00-09:00) and midday (12:00-13:00) schedules/traffic conditions. The grid cells are compatible with the statistical 
grid cells in the YKR (yhdyskuntarakenteen seurantajärjestelmä) data set produced by the Finnish Environment Institute (SYKE). 

The CO2 emissions are calculated based on the distance that is travelled with different travel modes (private car & PT) on a individual route multiplied with a specific carbon emission factors.
Carbon emission factors are based on the same estimates that Helsinki Region Transport (HRT) uses in their [Journey Planner service](http://www.reittiopas.fi/en/), more info [here](http://www.hsljalki.fi/en/menu/info).
Public transportation emissions are a sum of emissions based on bus, tram, metro, ferry and train.
   
Dataset is openly available for everyone for free and it can be downloaded from the [Accessibility Research Group website](http://www.helsinki.fi/science/accessibility/data) (under a Creative Commons 4.0 Licence).

Helsinki Region Travel CO2 Matrix 2015 is closely related to __[Helsinki Region Travel Time Matrix 2015](http://blogs.helsinki.fi/saavutettavuus/paakaupunkiseudun-matka-aikamatriisi-2015/)__ 
that is also produced by Accessibility Research Group. 
More information on how the Helsinki Region Travel Time Matrix 2015 was calculated can be found [from here](https://github.com/AccessibilityRG/HelsinkiRegionTravelTimeMatrix2015). 
 
__Scientific examples__ of the approach used here can be read from the following articles:

- Lahtinen, J., Salonen, M. & Toivonen, T. (2013). [Facility allocation strategies and the sustainability of service delivery: 
Modelling library patronage patterns and their related CO2-emissions](http://www.sciencedirect.com/science/article/pii/S014362281300163X). Applied Geography 44, 43-52.

- Salonen, M. & Toivonen, T. (2013). [Modelling travel time in urban networks: comparable measures for private car and public transport.](http://www.sciencedirect.com/science/article/pii/S096669231300121X) Journal of Transport Geography 31, 143–153.

## <a name="attributes"></a>Attributes of Helsinki Region Travel CO2 Matrix 2015

| Attribute | Definition |
| --------- | ---------- | 
| __from_id__   | ID number of the origin grid cell |
| __to_id__     | ID number of the destination grid cell |
| __pt_r_co2__  | CO2 emissions (grams/passenger) of the route by public transportation in rush hour traffic | 
| __pt_r_dd__   | Distance (meters) of the route travelled by any public transportation vehicle in rush hour traffic | 
| __pt_r_l__    | Number of lines used on the route by public transportation in rush hour traffic |
| __pt_m_co2__  | CO2 emissions (grams/passenger) of the route by public transportation in midday traffic |
| __pt_m_dd__   | Distance (meters) of the route travelled by any public transportation vehicle in midday traffic | 
| __pt_m_l__    | Number of lines used on the route by public transportation in midday traffic |
| __car_r_co2__ | CO2 emissions (grams/vehicle) of the route by private car in rush hour traffic |
| __car_r_dd__  | Distance (meters) driven by car during in rush hour traffic |
| __car_r_fc__  | Estimated fuel consumption (liters) by car during in rush hour traffic |
| __car_m_co2__ | CO2 emissions (grams/vehicle) of the route by private car in midday traffic |
| __car_m_dd__  | Distance (meters) driven by car in midday traffic |
| __car_m_fc__  | Estimated fuel consumption (liters) by car in midday traffic |

 
## <a name="calculations"></a>How calculations were done?

CO2 and fuel consumption calculations are based on travel distances by different transport modes that are multiplied by [carbon emission factors or fuel consumption estimates](http://www.hsljalki.fi/en/menu/info). 
Travel distances for each route are calculated using specific accessibility GIS tools called __[MetropAccess-Reititin](http://blogs.helsinki.fi/accessibility/reititin/)__ and __[MetropAccess-Digiroad](http://blogs.helsinki.fi/accessibility/digiroad-tool/)__ that are developed and maintained by Accessibility Research Group, Uni. Helsinki.
 
The routes by __car__ have been calculated in ArcGIS 10.2 software by using the OD Cost Matrix tool in the Network Analyst toolkit. MetropAccess-Digiroad (modified from the original Digiroad data
provided by Finnish Transport Agency) has been used as Network Dataset in which the route selection/optimization are made more realistic by adding crossroad impedances for different road classes. 
The calculations have been repeated for two times of the day using 1) the "midday impedance" (i.e. travel times outside rush hour) and 2) the "rush hour impendance" as impedance in the calculations.

All trip legs where car is used are taken into account in the calculations: 
 1. travel distance from parking lot to destination 
 2. average travel distance for searching a parking lot 

The routes by __public transportation__ have been calculated by using the MetropAccess-Reititin tool which also takes into account the whole travel chains from the origin to the destination. 
In CO2 calculations only trip legs that the passenger travels with any vehicle are taken into account:
 1. travel distance to next transit stop, 
     1. possible transport mode change, 
 2. travel distance to next transit stop (continuing until the last stop is reached)

Travel distance calculations by public transportation have been optimized by using 10 different departure times within the calculation hour using so called Golomb ruler. 
The fastest route from these calculations are selected for the final travel CO2 matrix.

Calculations of Helsinki Region Travel CO2 Matrix 2015 are based on schedules of Monday 28.09.2015 at:
 1. Midday (optimized between 12:00-13:00) 
 2. Rush hour (optimized between 08:00-09:00)

### <a name="co2-calculations">CO2 calculations

In the CO2 calculations, the travel distances by public transportation includes all trip legs that are done with any vehicle (i.e. bus, train, metro, tram, ferry), thus walking is excluded. 
CO2 values for each trip leg and for each transport mode are calculated separately and then summed together. As Helsinki Region Public Transport is mainly CO2 free, __the only transport modes
that actually causes CO2 emissions are bus (73 g/km) and ferry (389 g/km)__. The number of passengers on buses is estimated to be on average 13 passengers per bus. Final CO2 emission for public transport and car are calculated separately with function:
    
    Distance(km) * carbonEmissionFactor
 
Travel distances by private car takes into account the actual driving distance between origin and destination location 
and the distance that it approximately takes to find a parking place at the destination. __Carbon emission factor for private car is 171 g/km__.   
More information about the car distance calculations can be found from [here](http://blogs.helsinki.fi/accessibility/digiroad-tool/). 

### <a name="fc-calculations">Fuel consumption calculations
Fuel consumption calculations (for private car) are also based on driving distance between origin and 
destination locations plus additional distance that it takes to find a parking place (i.e. a single route). 

Average fuel consumption of a car is depending on various factors such as:
 
 - age and size of the car
 - fuel that is used (petrol vs diesel)
 - weather conditions (summer vs winter)
 - traffic conditions (city center vs rural highway)
   
Thus, it is rather impossible to calculate "accurate" and static fuel consumption for a car, let alone for all cars in Helsinki Region. 
Hence, the average fuel consumption used in the matrix is a compromise and a heavily simplified measure.  
__Fuel consumption for all cars is estimated as 7.3 liters per 100 kilometers__ that is the average fuel consumption of all different 
sizes of cars (small, midsize, large), and all different ages of cars (0-5 years, 6-10 years, 10+ years), and all cars using either petrol or diesel as fuel. 
Fuel consumption estimates were retrieved from the [table](http://www.hsljalki.fi/en/menu/info) that is used by HRT to calculate the CO2 emissions.     
The fuel consumption estimates are based on the [LIPASTO](http://lipasto.vtt.fi/en/liisa/fuel.htm) calculation system of the Technical Research Centre of Finland (VTT).
      
The estimated fuel consumption per route is calculated with following formula (example for rush hour fuel consumption):

    (car_r_dd / 100000.0) * 7.3

Using the above formula it is also possible to estimate the fuel consumption of routes by using a different fuel consumption factor (here 7.3 liters / 100 km).   

## <a name="license"></a>Licence

Helsinki Region Travel CO2 Matrix 2015 by Accessibility Research Group (University of Helsinki) is licensed under a Creative Commons Attribution 4.0 International License. 
More information about license: http://creativecommons.org/licenses/by/4.0/

If the datasets are being used extensively in scientific research, we welcome the opportunity for co-authorship of papers. Please contact project leader to discuss about the matter.

## <a name="how-to-cite"></a>Citation practices

If you use Helsinki Region Travel CO2 Matrix 2015 dataset or related tools in your work, we encourage you to cite properly to our work.

You can cite to our work as follows:

__Data/Tools description:__

- Toivonen, T., M. Salonen, H. Tenkanen, P. Saarsalmi, T. Jaakkola & J. Järvi (2014). 
Joukkoliikenteellä, autolla ja kävellen: Avoin saavutettavuusaineisto pääkaupunkiseudulla. Terra 126: 3, 127-136. 

__DOI name for the dataset:__

- Toivonen, T., H. Tenkanen, V. Heikinheimo, T. Jaakkola, J. Järvi & M. Salonen (2016). Helsinki Region Travel CO2 Matrix 2015. DOI: 10.13140/RG.2.1.2601.0648 

## <a name="codes"></a>Codes

All the codes and analysis steps that have been used to produce the Helsinki Region Travel CO2 Matrix 2015 are documented separately in [here](codes/README.md). 

## <a name="contact"></a>Contribution / Contact
Helsinki Region Travel CO2 Matrix 2015 was created by the [Accessibility Research Group](http://www.helsinki.fi/science/accessibility) 
at the Department of Geosciences and Geography, University of Helsinki, Finland.
 
Following people have contributed / are responsible for creating this dataset:

 - [Henrikki Tenkanen](http://blogs.helsinki.fi/accessibility/people_and_contact/) (PhD candidate, contact person regarding the dataset, in charge of the analyses / calculations)
 - Vuokko Heikinheimo (PhD candidate, accessibility calculations, documentation)
 - Jaani Lahtinen (PhD candidate / private consultant (Gispositio Oy), programming and design of CO2 calculator (RouteCarbonCalculator.jar)
 - Tuuli Toivonen (PI, leader of the research group)
 
In addition, we thank [CSC - IT Center for Science](https://www.csc.fi/) for computational resources and help. 
CSC Taito and cPouta computing clusters were used as our workhorses to calculate the travel times/distances (approx. 1 billion routes were calculated) 
using MetropAccess-Digiroad- and MetropAccess-Reititin Tools.   