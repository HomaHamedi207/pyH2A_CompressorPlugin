import numpy as np

class TestingDCF:
    def __init__(self):
        
        self.inp = {
            'Water Volume': {'Volume': {'Value': 50, 'Unit': 'liters'}},  
            'Number of units': {'Bag number': {'Value': 50, 'Unit': 'dimensionless'}},  
            'Catalyst': {'Lifetime': {'Value': 5, 'Unit': 'years'}} ,
            'Catalyst Separation': {'Filtration cost': {'Value': 100, 'Unit': '$/m3'}},
            'Grid electricity': {'Cost': {'Value': 0.15, 'Unit': '$/kWh'}},
            # The following one's values are dictionaries of floats or of arrays of floats
            'Power Generation': {
                                'Available Power': {'Value': {'2025':np.array([400., 250., 350.]), '2024':np.array([500., 350., 450.])}, 'Unit': 'kWh'},
                                'Stored Power': {'Value': {'2025': 200., '2024': 250.}, 'Unit': 'kWh'}
                                },
            # the following one serves to test the situation where middle key isn't known in advance / when we want to iterate
            'Power Consumption': {
                'Any mid key': {'Value': np.array([100., 120., 110.]),'Type': 'on demand','Unit': 'kWh'},
                'Another mid key': {'Value': np.array([50., 40., 60.]), 'Type': 'flexible','Unit': 'kWh'},
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
                         'mid_level' : {
                            'Volume':{
                                'item_schema': {                    
                                    'Value': {
                                        'type': {float,},
                                        'bounds': (0, None),
                                    },
                                    'Unit': {'dimension': 'volume',},                    
                                 },
                                'optional': False,
                                'description': 'Total water volume in liters.'
                            },                                                        
                        },
    },
    
    'Bag_number': {'top_level': 'Number of units',
                         'mid_level' : {
                            'Bag number':{
                                'item_schema': {                    
                                    'Value': {
                                        'type': {int,},
                                        'bounds': (0, None),
                                    },
                                    'Unit': {'dimension': 'dimensionless',},                    
                                 },
                                'optional': False,
                                'description': 'Number of bags in the system.'
                            },                                                        
                        },
    },

    'Catalyst_lifetime': {'top_level': 'Catalyst',
                         'mid_level' : {
                            'Lifetime':{
                                'item_schema': {                    
                                    'Value': {
                                        'type': {float,},
                                        'bounds': (0, None),
                                    },
                                    'Unit': {'dimension': 'time',},                    
                                 },
                                'optional': False,
                                'description': 'Catalyst lifetime in years.'
                            },                                                        
                        },
    },

    'Catalyst_Separation': {'top_level': 'Catalyst Separation',
                         'mid_level' : {
                            'Filtration cost':{
                                'item_schema': {                    
                                    'Value': {
                                        'type': {float,},
                                        'bounds': (0, None),
                                    },
                                    'Unit': {'dimension': 'money_per_volume',},                    
                                 },
                                'optional': False,
                                'description': 'Specific Catalyst separation cost.'
                            },                                                        
                        },
    },
    
    'grid_electricity_cost': {'top_level': 'Grid Electricity',
                         'mid_level' : {
                            'Cost':{
                                'item_schema': {                    
                                    'Value': {
                                        'type': {float, np.ndarray}, # I kept things simple for the moment: just check that the value is one of the types specified in the set. We don't check the type of the eventual nested structure
                                        'bounds': (0, None),
                                    },
                                    'Unit': {'dimension': 'money_per_energy',},                    
                                 },
                                'optional': True,
                                'description': 'Stored electric energy per period.'
                            },                                                        
                        },
    },

    'Power_Generation': {'top_level': 'Power Generation',
                         'mid_level' : {
                            'Stored Power':{
                                'item_schema': {                    
                                    'Value': {
                                        'type': {dict,},
                                        'bounds': (0, None),
                                    },
                                    'Unit': {'dimension': 'energy',},                    
                                 },
                                'optional': True,
                                'description': 'Stored electric energy per period.'
                            },
                            'Available Power':{
                                'item_schema': {                    
                                    'Value': {
                                        'type': {dict,}, 
                                        'bounds': (0, None),
                                    },
                                    'Unit': {'dimension': 'energy',},                    
                                },     
                                'optional': False,
                                'description': 'Available electric energy per period.'
                            },                                                         
                        },
    },

    'power_consumption': {'top_level': 'Power Consumption',
                         'mid_level' : {
                            '<...>':{ # refers to the case when the middle key isn't known in advance
                                'item_schema': {                    # Assuming all the keys that are not known in advance must follow the same schema
                                    'Value': {
                                        'type': {np.ndarray,},
                                        'bounds': (0, None),
                                        'length': 3 # expected length of the array (in practice, would be more like 365 for a value per day of the year)
                                    },
                                    'Unit': {'dimension': 'energy',},   
                                    'Type': {
                                        'type': {str,},
                                        'options': {'on demand', 'flexible'},                                    
                                    },
                                },                                     
                                'optional': True,
                                'description': 'Power consumption per consumer.'
                            },                                                        
                        },
    },
    
     'other_variable_operating_cost': {'top_level': '<...> Other Variable Operating Cost <...>', # table group
                         'mid_level' : {
                            '<...>':{ 
                                'item_schema': {                    
                                    'Value': {
                                        'type': {float, np.ndarray},
                                        'bounds': (0, None),
                                        # length might not be known in advance: check its consistency only if the 'length' key is found in the input
                                    },
                                    'Unit': {'dimension': 'money',},   
                                },                                     
                                'optional': True,
                                'description': 'All other variable operating costs.'
                            },                                                        
                        },
    }         
                    
}

                     