# Workflow

Name | Type | Description | Position
--- | --- | --- | ---
Hourly_Irradiation_Plugin | plugin | Plugin to calculate solar irradiation from typical meteorological year data | 0
Solar_Thermal_Plugin | plugin | Computes land area required for thermal process | 2
Multiple_Modules_Plugin | plugin | Modelling of multiple plant modules, adjustment of labor requirement | 3

# Construction

Name | Value
--- | ---

# Hourly Irradiation

Name | Value 
--- | --- 
File | pyH2A.Lookup_Tables.Hourly_Irradiation_Data~tmy_34.859_-116.889_2006_2015.csv

# Irradiance Area Parameters

Name | Value | Comment
--- | ---  | --- 
Nominal Operating Temperature (Celsius) | 20.0 | 
Mismatch Derating | 0.95 | 
Dirt Derating | 0.9 | 
Temperature Coefficient (per Celsius) | 0.0 | 
Module Tilt (degrees) | 10. | 
Array Azimuth (degrees) | 10. | 

# Solar Input 

Name | Value | Comment
--- | ---  | --- 
Mean solar input (kWh/m2/day) | 4 | 

# Solar-to-Hydrogen Efficiency

Name | Value  | Comment
--- | ---  | --- 
STH (%) | 4. | 

# Technical Operating Parameters and Specifications

Name | Value 
--- | --- 
Plant Design Capacity (kg of H2/day) | 1200.
Operating Capacity Factor (%) | 30.
Plant Modules | 10.

# Non-Depreciable Capital Costs 

Name | Value 
--- | --- 
Cost of land ($ per acre) | 10.
Additional Land Area (%) | 30.0% 
Solar Collection Area (m2) | 70000 | should probably be calculated somewhere else

# Fixed Operating Costs

Name | Value 
--- | --- 
hourly labor cost | 12.
area | 2500
supervisor | 1
shifts | 5

# Utilities

# Planned Replacement
