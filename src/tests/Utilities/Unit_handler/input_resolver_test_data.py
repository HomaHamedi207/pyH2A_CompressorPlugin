
class TestingDCF:
    def __init__(self):
        
        self.inp = {
            'Water Volume': {'Volume': {'Value': 50, 'Unit': 'liters'}},  
            'Number of units': {'Bag number': {'Value': 50, 'Unit': 'dimensionless'}},  
            'Catalyst': {'Lifetime': {'Value': 5, 'Unit': 'years'}} ,
            'Catalyst Separation': {'Filtration cost': {'Value': 100, 'Unit': '$/m3'}},
            'Grid electricity': {'Cost': {'Value': 0.15, 'Unit': '$/kWh'}},
            'Power Generation': {
                                'Available Power': {'Value': np.array([400., 250., 350.]), 'Unit': 'kWh'},
                                'Stored Power': {'Value': np.array([200., 50., 150.]), 'Unit': 'kWh'}
                                },
            # the following one serves to test the situation where middle key isn't known in advance / when we want to iterate
            'Power Consumption': {
                'Any mid key': {'Value': np.array([100., 120., 110.]),'Type': 'on demand','Unit': 'kWh'},
                'Another mid key': {'Value': np.array([50., 40., 60.]), 'Type': 'flexible','Unit': 'kWh'}                             
                                }, 
            # Pump and compressor: to test the "Other Variable Operating Cost" group
            'Pump - Other Variable Operating Cost - Brand A': {
                'Maintenance': {'Value': 12.5},
                'lubrication':  {'Value': 8.2}
            },
            'Compressor - Other Variable Operating Cost - Brand B': {
                'Lubrication': {'Value': np.array([1.3, 1.2, 1.1])},
                'Electricity': {'Value': 2.2}                
            }
                                
                    }

input_dict = {
    'water_volume': {'top_level': 'Water Volume',
                     'mid_level': 'Volume',
                     'lower_level': 'Value',
                     'dimension': 'volume',
                     'type': float,
                     'optional': False,
                     'bounds': (0, None),
                     'description': 'Total water volume in liters.'},
                     
    'Bag_number': {'top_level': 'Number of units',
                     'mid_level': 'Bag number',
                     'lower_level': 'Value',
                     'dimension': 'dimensionless',
                     'type': int,
                     'optional': False,
                     'bounds': (0, None),
                     'description': 'Number of bags in the system.'},
                     
    'Catalyst_lifetime': {'top_level': 'Catalyst',
                     'mid_level': 'Lifetime',
                     'lower_level': 'Value',
                     'dimension': 'time',
                     'type': float,
                     'optional': False,
                     'bounds': (0, None),
                     'description': 'Catalyst lifetime in years.'},
                     
    'Catalyst_Separation': {'top_level': 'Catalyst Separation',
                     'mid_level': 'Filtration cost',
                     'lower_level': 'Value',
                     'dimension': 'money_per_volume',
                     'type': float,
                     'optional': False,
                     'bounds': (0, None),
                     'description': 'Specific Catalyst separation cost.'},        

    'power_available': {'top_level': 'Power Generation',
                    'mid_level': 'Available Power',
                    'lower_level': 'Value',
                    'dimension': 'energy',
                    'type': np.ndarray,
                    'optional': False,
                    'bounds': (0, None),
                    'description': 'Available electric energy per period (length 3).'},                 
                      
    'grid_electricity_cost': {'top_level': 'Grid Electricity',
                     'mid_level': 'Cost',
                     'lower_level': 'Value',
                     'dimension': 'money_per_energy',
                     'type': {float, np.ndarray}, # will allow to check if the observed type of an instance matches an element of the set. I wonder if we should declare it as a tuple (np.ndarray, float) so we can chack: if it's an array (first tuple element), are the elements of the array floats (second tuple element)?
                     'optional': True,
                     'bounds': (0, None),
                     'description': 'Cost of grid electricity in $/kWh'},        
   
                    
    'power_stored': {'top_level': 'Power Generation',
                    'mid_level': 'Stored Power',
                    'lower_level': 'Value',
                    'dimension': 'energy',
                    'type': np.ndarray,
                    'optional': True,
                    'bounds': (0, None),
                    'description': 'Stored electric energy per period (length 3).'}, 
    
    'power_consumption': {'top_level': 'Power Consumption',
                    'kind': 'collection', # refers to the case when the middle key isn't known in advance
                    'item_schema': {
                        'Value': {
                            'type': np.ndarray,
                            'bounds': (0, None),
                            'length': 3,
                            'dimension': 'energy'
                        },
                        'Type': {
                            'type': str,
                            'allowed': {'on demand', 'flexible'}
                        }
                    },
                    'optional': True,
                    'description': 'Power consumption per consumer.'},                   

    'other_variable_operating_cost': {
                    'table_group': 'Other Variable Operating Cost', # Pattern to be recognized as being in the group 
                    'kind': 'collection',
                    'item_schema': {
                        'Value': {
                            'type': {float, np.ndarray},
                            'bounds': (0, None),
                            'dimension': 'money'
                        }
                    },
                    'optional': True,
                    'description': 'All other variable operating costs.'}
                     
    }

                     