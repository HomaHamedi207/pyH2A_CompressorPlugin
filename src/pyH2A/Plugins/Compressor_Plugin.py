from pyH2A.Utilities.input_modification import insert, process_table
import numpy as np

class Compressor_Plugin:
    '''Simulation of hydrogen gas compression for storage and transport.

    Parameters
    ----------
    Compressor > Inlet Pressure (bar) > Value : float
        Inlet pressure of hydrogen gas in bar.
    Compressor > Outlet Pressure (bar) > Value : float
        Outlet pressure of hydrogen gas in bar.
    Compressor > Isentropic Efficiency (%) > Value : float
        Isentropic efficiency of compressor. Percentage or value between 0 and 1.
    Compressor > Number of Stages > Value : int, optional
        Number of compression stages. If not provided, it is automatically estimated
        so the per-stage compression ratio is approximately <= 10.
    Compressor > Unit CAPEX ($ per kW) > Value : float, optional
        Unit capital cost in dollars per kW of compressor power. If not provided,
        a default value based on literature estimates will be used.
    Compressor > CAPEX Reference Power (kW) > Value : float, optional
        Reference power for CAPEX scaling. Used with CAPEX Multiplier to account
        for economies of scale.
    CAPEX Multiplier > Multiplier > Value : float, optional
        Multiplier to describe cost reduction of compressor CAPEX for every ten-fold
        increase of power relative to CAPEX reference power. Based on the multiplier the CAPEX
        scaling factor is calculated as: multiplier ^ (number of ten-fold increases). A value
        of 1 leads to no CAPEX reduction, a value < 1 enables cost reduction.
    Electrolyzer > H2 Production (yearly, kg) > Value : nd.array
        Yearly hydrogen production in kg from electrolyzer (if using Electrolyzer_Plugin).
    Photoelectrochemical > H2 Production (yearly, kg) > Value : nd.array
        Yearly hydrogen production in kg from PEC system (if using PEC_Plugin).

    Returns
    -------
    Compressor > Power Consumption (yearly, kWh) > Value : nd.array
        Yearly power consumption for hydrogen compression in kWh.
    Compressor > Compression Ratio > Value : float
        Pressure ratio between outlet and inlet pressure.
    Compressor > Power Consumption per kg H2 (kWh/kg) > Value : float
        Average power consumption per kg of hydrogen produced.
    Compressor > Number of Stages > Value : int
        Number of compressor stages used in the calculation.
    Compressor > Stage Compression Ratio > Value : float
        Compression ratio per stage for equal-ratio staging.
    Compressor > CAPEX ($) > Value : float
        Estimated capital cost of the compressor system in dollars.
        
    Notes
    -----
    To include compressor electricity costs in the economic analysis, add a utility
    entry in your input data with the compressor power consumption per kg H2:
    
    Utilities > Compressor Electricity > Usage per kg H2 > Value
        Should be set to the value from "Compressor > Power Consumption per kg H2 (kWh/kg)"
    Utilities > Compressor Electricity > Cost > Value
        Electricity cost in $/kWh
    '''

    def __init__(self, dcf, print_info):
        process_table(dcf.inp, 'Compressor', 'Value')
        
        # Process CAPEX Multiplier table if it exists
        if 'CAPEX Multiplier' in dcf.inp:
            process_table(dcf.inp, 'CAPEX Multiplier', 'Value')
        
        self.hours_in_a_year = 8760

        self.calculate_compression(dcf)
        self.calculate_capex(dcf)

        insert(dcf, 'Compressor', 'Compression Ratio', 'Value',
                self.compression_ratio, __name__, print_info=print_info)
        insert(dcf, 'Compressor', 'Number of Stages', 'Value',
            self.number_of_stages, __name__, print_info=print_info)
        insert(dcf, 'Compressor', 'Stage Compression Ratio', 'Value',
            self.stage_compression_ratio, __name__, print_info=print_info)
        insert(dcf, 'Compressor', 'H2 Production (yearly, kg)', 'Value', 
            self.h2_production_yearly, __name__, print_info=print_info)
        insert(dcf, 'Compressor', 'Power Consumption (yearly, kWh)', 'Value',
            self.yearly_power_consumption_kwh, __name__, print_info=print_info)
        insert(dcf, 'Compressor', 'Average Power Consumption (yearly, kWh)', 'Value',
            np.mean(self.yearly_power_consumption_kwh), __name__, print_info=print_info)
        insert(dcf, 'Compressor', 'Power Consumption (kW)', 'Value',
                self.power_consumption, __name__, print_info=print_info)
        insert(dcf, 'Compressor', 'Power Consumption per kg H2 (kWh/kg)', 'Value',
                self.power_per_kg_h2, __name__, print_info=print_info) 
        insert(dcf, 'Compressor', 'CAPEX ($)', 'Value',
                self.compressor_capex, __name__, print_info=print_info)
        
          
        
    def calculate_compression(self, dcf):
        '''Calculate power required for hydrogen compression using the isentropic
        compression work equation for ideal gas. Reads H2 production from either
        Electrolyzer or PEC systems.
        '''

        # Try to read H2 production from Electrolyzer first
        if 'Electrolyzer' in dcf.inp and 'H2 Production (yearly, kg)' in dcf.inp['Electrolyzer']:
            self.h2_production_yearly = dcf.inp['Electrolyzer']['H2 Production (yearly, kg)']['Value']
        else:
            # For PEC/PC systems, calculate H2 from design output and operating capacity factor
            design_output_per_day = dcf.inp['Technical Operating Parameters and Specifications']['Design Output per Day']['Value']
            operating_capacity_factor = dcf.inp['Technical Operating Parameters and Specifications']['Operating Capacity Factor (%)']['Value']
            
            # Annual H2 production = daily design output * 365 days * capacity factor
            self.h2_production_yearly = design_output_per_day * 365 * operating_capacity_factor * np.ones(len(dcf.operation_years))
        
        inlet_pressure = dcf.inp['Compressor']['Inlet Pressure (bar)']['Value']
        outlet_pressure = dcf.inp['Compressor']['Outlet Pressure (bar)']['Value']
        isentropic_efficiency = dcf.inp['Compressor']['Isentropic Efficiency (%)']['Value']
        # Calculate compression ratio
        self.compression_ratio = outlet_pressure / inlet_pressure

        # Isentropic work for hydrogen compression (kWh/kg)
        # For hydrogen: gamma = 1.41, specific gas constant R = 4.124 kJ/(kg·K), T_inlet ≈ 288 K
        gamma = 1.41
        R = 4.124  # kJ/(kg·K)
        T_inlet = 288.15  # K (15°C)

        if 'Number of Stages' in dcf.inp['Compressor']:
            self.number_of_stages = int(dcf.inp['Compressor']['Number of Stages']['Value'])
            if self.number_of_stages < 1:
                self.number_of_stages = 1
        else:
            stage_ratio = 3.0  # typical with intercooling
            self.number_of_stages = max(1, int(np.ceil(np.log(self.compression_ratio) / np.log(stage_ratio))))

        self.stage_compression_ratio = self.compression_ratio ** (1.0 / self.number_of_stages)

        # Equal-ratio staged compression with intercooling between stages
        # Isentropic work per stage: W_s = (gamma/(gamma-1)) * R * T_inlet * (r_stage^((gamma-1)/gamma) - 1)
        isentropic_exponent = (gamma - 1) / gamma
        W_isentropic_stage = (gamma / (gamma - 1)) * R * T_inlet * (
            self.stage_compression_ratio ** isentropic_exponent - 1
        )  # kJ/kg
        W_isentropic = self.number_of_stages * W_isentropic_stage  # kJ/kg

        # Convert to kWh/kg and apply efficiency
        W_isentropic_kWh = W_isentropic / 3600  # kJ/kg to kWh/kg
        actual_work = W_isentropic_kWh / isentropic_efficiency  # Account for efficiency losses
        
        # Store power consumption per kg H2 for use in Utilities
        self.power_per_kg_h2 = actual_work  # kWh/kg
        
        # Calculate yearly and average power consumption
        self.yearly_power_consumption_kwh = self.h2_production_yearly * actual_work  # kWh/year
        self.power_consumption = self.yearly_power_consumption_kwh / self.hours_in_a_year  # kW average for each year

    def calculate_capex(self, dcf):
        '''Calculate compressor capital cost based on power rating.
        
        Uses unit CAPEX ($/kW) and maximum power consumption. Optionally applies
        economies of scale using CAPEX multiplier and reference power.
        
        Default unit CAPEX is based on multi-stage reciprocating compressor estimates
        for hydrogen service, including intercoolers and auxiliaries.
        '''
        
        # Get max power for sizing
        max_power_kw = np.max(self.power_consumption)
        
        # Default unit CAPEX if not provided ($/kW)
        # Literature values for multi-stage H2 compressors: $75/kW
        # Adjusted for stages and intercoolers
        default_unit_capex = 75.0 + (self.number_of_stages - 1) * 15.0  # Additional cost per stage
        
        if 'Unit CAPEX ($ per kW)' in dcf.inp['Compressor']:
            unit_capex = dcf.inp['Compressor']['Unit CAPEX ($ per kW)']['Value']
        else:
            unit_capex = default_unit_capex
        
        # CAPEX calculation
        self.compressor_capex = unit_capex * max_power_kw
        

    
