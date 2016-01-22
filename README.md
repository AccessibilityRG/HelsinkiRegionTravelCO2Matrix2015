# Helsinki Region Travel CO2 Matrix 2015

This repository demonstrates / documents how [Helsinki Region Travel CO2 Matrix 2015](http://www.helsinki.fi/science/accessibility/data) is calculated. 
Dataset was produced by [Accessibility Research Group](http://www.helsinki.fi/science/accessibilty), University of Helsinki.

## What is Helsinki Region Travel CO2 Matrix 2015
 
[__Helsinki Region Travel CO2 Matrix 2015__](http://www.helsinki.fi/science/accessibility/data) is a dataset that contains CO2 emissions (+some additional attributes) produced by public transportation (PT) and private car
for routes between all 250 m x 250 m grid cell centroids (n = 13231) in the Capital Region of Helsinki. Calculations were done separately for two different time of the day using 
rush hour (08:00-09:00) and midday (12:00-13:00) schedules/traffic conditions. The grid cells are compatible with the statistical 
grid cells in the YKR (yhdyskuntarakenteen seurantajärjestelmä) data set produced by the Finnish Environment Institute (SYKE). 

The CO2 emissions are calculated based on the distance that is travelled with different travel modes (private car & PT) on a individual route multiplied with a specific carbon emission factors.
Carbon emission factors are based on the same estimates that Helsinki Region Transport (HRT) uses in their [Journey Planner service](http://www.reittiopas.fi/en/), more info [here](http://www.hsljalki.fi/en/menu/info).
Public transportation emissions are a sum of emissions based on bus, tram, metro, ferry and train.
Final CO2 emission for public transport and car are calculated separately with function:
    
    Distance(km) * carbonEmissionFactor
   
Dataset is openly available for everyone for free and it can be downloaded from the [Accessibility Research Group website](http://www.helsinki.fi/science/accessibility/data) (under a Creative Commons 4.0 Licence).

Helsinki Region CO2 Matrix 2015 is closely related to __[Helsinki Region Travel Time Matrix 2015](http://blogs.helsinki.fi/saavutettavuus/paakaupunkiseudun-matka-aikamatriisi-2015/)__ 
that is also produced by Accessibility Research Group. 
More information how the Helsinki Region Travel Time Matrix 2015 was calculated can be found [here](). 
 
__Scientific examples__ of the approach used here can be read from the following articles:

- Lahtinen, J., Salonen, M. & Toivonen, T. (2013). [Facility allocation strategies and the sustainability of service delivery: 
Modelling library patronage patterns and their related CO2-emissions](http://www.sciencedirect.com/science/article/pii/S014362281300163X). Applied Geography 44, 43-52.

- Salonen, M. & Toivonen, T. (2013). [Modelling travel time in urban networks: comparable measures for private car and public transport.](http://www.sciencedirect.com/science/article/pii/S096669231300121X) Journal of Transport Geography 31, 143–153.

## Attributes of Helsinki Region Travel CO2 Matrix 2015

| Attribute | Definition |
| --------- | ---------- | 
| from_id   | ID number of the origin grid cell |
| to_id     | ID number of the destination grid cell |
| pt_r_co2  | CO2 emissions of the route by public transportation in rush hour traffic | 
| pt_r_dd   | Distance of the route travelled by any public transportation vehicle in rush hour traffic | 
| pt_r_l    | Number of lines used on the route by public transportation in rush hour traffic |
| pt_m_co2  | CO2 emissions of the route by public transportation in midday traffic |
| pt_m_dd   | Distance of the route travelled by any public transportation vehicle in midday traffic | 
| pt_r_l    | Number of lines used on the route by public transportation in midday traffic |
| car_r_co2 | CO2 emissions of the route by private car in rush hour traffic |
| car_r_dd  | Distance driven by car during in rush hour traffic |
| car_r_fc  | Estimated fuel consumption by car during in rush hour traffic |
| car_r_co2 | CO2 emissions of the route by private car in midday traffic |
| car_r_dd  | Distance driven by car in midday traffic |
| car_r_fc  | Estimated fuel consumption by car in midday traffic |

 
## How calculations were done?

CO2 and fuel consumption calculations are based on travel distances by different transport modes that are multiplied by [carbon emission factors or fuel consumption estimates](http://www.hsljalki.fi/en/menu/info). 
Travel distances for each route are calculated using specific accessibility GIS tools called __[MetropAccess-Reititin](http://blogs.helsinki.fi/accessibility/reititin/)__ and __[MetropAccess-Digiroad](http://blogs.helsinki.fi/accessibility/digiroad-tool/)__ that are developed and maintained by Accessibility Research Group, Uni. Helsinki. 

### CO2 calculations

In the CO2 calculations, the travel distances by public transportation includes all trip legs that are done with any vehicle (i.e. bus, train, metro, tram, ferry), thus walking is excluded. 
CO2 values for each trip leg and for each transport mode are calculated separately and then summed together. As Helsinki Region Public Transport is mainly CO2 free, the only transport modes
that actually causes CO2 emissions are bus (73 g/km) and ferry (389 g/km). 
 
Travel distances by private car takes into account the actual driving distance between origin and destination location 
and the distance that it approximately takes to find a parking place at the destination. Carbon emission factor for private car is 171 g/km.   
More information about the car distance calculations can be found from [here](http://blogs.helsinki.fi/accessibility/digiroad-tool/). 

### Fuel consumption calculations
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
sizes of cars (small, midsize, large) and all different ages of cars (0-5 years, 6-10 years, 10+ years), and all cars using either petrol or diesel as fuel. 
Fuel consumption estimates were retrieved from the [table](http://www.hsljalki.fi/en/menu/info) that is used by HRT to calculate the CO2 emissions.     
The fuel consumption estimates are based on the [LIPASTO](http://lipasto.vtt.fi/en/liisa/fuel.htm) calculation system of the Technical Research Centre of Finland (VTT).
      
The estimated fuel consumption per route is calculated with following formula (example for rush hour fuel consumption):

    (car_r_dd / 100000.0) * 7.3

Using the above formula it is also possible to estimate the fuel consumption of routes by using a different fuel consumption factor (here 7.3 liters / 100 km).   

## Codes

1. [Parse CO2 emissions based on Helsinki Region Travel Time Matrix 2015 'raw' data](codes/README.md) 
