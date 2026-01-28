import numpy as np
from pint import UnitRegistry

ureg = UnitRegistry()
ureg.define('USD = [currency]')


class DummyDCF:
    def __init__(self):
        
        self.inp = {
            'Utilities': {
                'Natural gas': {
                    'Usage_Value': 1500,
                    'Usage_Unit': 'kWh/kg',
                    'Cost_Value': 200,
                    'Cost_Unit': 'USD/kWh',
                    'Type': 'natural_gas'
                },
                'Electricity': {
                    'Usage_Value': 3000,
                    'Usage_Unit': 'kWh/kg',
                    'Cost_Value': 500,
                    'Cost_Unit': 'USD/kWh',
                    'Type': 'electricity'
                }
            },        
            
            'Water Volume': {
                'Volume': {
                    'Value': 50, 
                    'Unit': 'liters'
                }
            },  
            
            'Number of units': {
                'Bag number': {
                    'Value': 50, 
                    'Unit': 'dimensionless'
                }
            },  
            
            'Catalyst': {
                'Lifetime': {
                    'Value': 5, 
                    'Unit': 'years'
                }
            } ,
            
            'Catalyst Separation': {
                'Filtration cost': {
                    'Value': 100, 
                    'Unit': '$/m3'
                }
            },
            
            'Grid electricity': {
                'Cost': {
                    'Value': 0.15, 
                    'Unit': '$/kWh'
                }
            },

            'Power Generation': {
                'Available Power': {
                    'Value': {
                        '2025':np.array([400., 250., 350.]), '2024':np.array([500., 350., 450.])
                    }, 
                    'Unit': 'kWh'
                },
                'Stored Power': {
                    'Value': {
                        '2025': 200., '2024': 250.
                    }, 
                        'Unit': 'kWh'
                    }
                },
                
            # the following one serves to test the situation where middle key isn't known in advance / when we want to iterate
            'Power Consumption': {
                'Any mid key': {
                    'Value': np.array([100., 120., 110.]),
                    'Type': 'on demand',
                    'Unit': 'kWh'
                },
                'Another mid key': {
                    'Value': np.array([50., 40., 60.]), 
                    'Type': 'flexible',
                    'Unit': 'kWh'
                },
            }, 
            
            # Pump and compressor: to test the "Other Variable Operating Cost" group
            'Pump - Other Variable Operating Cost - Brand A': {
                'Maintenance': {
                    'Value': 12.5, 
                    'Unit': '$'
                },
                'lubrication':  {
                    'Value': 8.2, 
                    'Unit': '$'
                }
            },
            
            'Compressor - Other Variable Operating Cost - Brand B': {
                'Lubrication': {
                    'Value': np.array([1.3, 1.2, 1.1]),
                    'Unit': '$'
                },
                'Electricity': {
                    'Value': 2.2, 
                    'Unit': '$'
                }                
            }
                                
        }

input_dict = {

    'utilities': {  'top_level': 'Utilities',
                    'mid_level': {
                        '<...>':{
                            'bottom_level': {
                                'Usage_Value': {
                                    'type': {float, int},
                                    'bounds': (0, None)
                                },
                                'Usage_Unit': {
                                    'dimension': 'energy / mass'
                                },
                                'Cost_Value': {
                                    'type': {float, int},
                                    'bounds': (0, None)
                                },
                                'Cost_Unit': {
                                    'dimension': 'currency / energy'
                                },
                                'Type': {
                                    'type': str,
                                    'options': {
                                        'electricity', 'natural_gas', 'water'
                                        },
                                }
                            },
                            'optional': True,
                            'description': 'The utility usage and cost details.'
                        },
                    },
    },

    'water_volume': {   'top_level': 'Water Volume',
                        'mid_level' : {
                            'Volume':{
                                'bottom_level': {                     
                                    'Value': {
                                        'type': {float,},
                                        'bounds': (0, None),
                                    },
                                    'Unit': {
                                        'dimension': 'volume'
                                    },                    
                                 },
                                'optional': False,
                                'description': 'Total water volume in liters.'
                            },                                                        
                        },
    },
    
    'Bag_number': {'top_level': 'Number of units',
                         'mid_level' : {
                            'Bag number':{
                                'bottom_level': {                    
                                    'Value': {
                                        'type': {int,},
                                        'bounds': (0, None),
                                    },
                                    'Unit': {
                                        'dimension': 'dimensionless',
                                    },                    
                                },
                                'optional': False,
                                'description': 'Number of bags in the system.'
                            },                                                        
                        },
    },

    'Catalyst_lifetime': {'top_level': 'Catalyst',
                         'mid_level' : {
                            'Lifetime':{
                                'bottom_level': {                    
                                    'Value': {
                                        'type': {float,},
                                        'bounds': (0, None),
                                    },
                                    'Unit': {
                                        'dimension': 'time'
                                    },                    
                                 },
                                'optional': False,
                                'description': 'Catalyst lifetime in years.'
                            },                                                        
                        },
    },

    'Catalyst_Separation': {'top_level': 'Catalyst Separation',
                            'mid_level' : {
                                'Filtration cost':{
                                    'bottom_level': {                    
                                        'Value': {
                                            'type': {float,},
                                            'bounds': (0, None),
                                        },
                                        'Unit': {
                                            'dimension': 'currency / volume'
                                        },                    
                                     },
                                    'optional': False,
                                    'description': 'Specific Catalyst separation cost.'
                                },                                                        
                            },
    },
    
    'grid_electricity_cost': {  'top_level': 'Grid Electricity',
                                'mid_level' : {
                                    'Cost':{
                                        'bottom_level': {                    
                                            'Value': {
                                                'type': {float, np.ndarray},
                                                'bounds': (0, None),
                                            },
                                            'Unit': {
                                                'dimension': 'currency / energy'
                                            },                    
                                        },
                                        'optional': True,
                                        'description': 'Stored electric energy per period.'
                                    },                                                        
                                },
    },

    'Power_Generation': {'top_level': 'Power Generation',
                         'mid_level' : {
                            'Stored Power':{
                                'bottom_level': {                    
                                    'Value': {
                                        'type': {dict,},
                                        'bounds': (0, None),
                                    },
                                    'Unit': {
                                        'dimension': 'energy'
                                    },                    
                                },
                                'optional': True,
                                'description': 'Stored electric energy per period.'
                            },
                            'Available Power':{
                                'bottom_level': {                    
                                    'Value': {
                                        'type': {dict,}, 
                                        'bounds': (0, None),
                                    },
                                    'Unit': {
                                        'dimension': 'energy'
                                    },                    
                                },     
                                'optional': False,
                                'description': 'Available electric energy per period.'
                            },                                                         
                        },
    },

    'power_consumption': {'top_level': 'Power Consumption',
                         'mid_level' : {
                            '<...>':{   
                                'bottom_level': {                    # Assuming all the keys that are not known in advance must follow the same schema
                                    'Value': {
                                        'type': {np.ndarray,},
                                        'bounds': (0, None),
                                        'length': 3 # expected length of the array (in practice, would be more like 365 for a value per day of the year)
                                    },
                                    'Unit': {
                                        'dimension': 'energy'
                                    },   
                                    'Type': {
                                        'type': {str,},
                                        'options': {
                                            'on demand', 'flexible'
                                        },                                    
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
                                                'bottom_level': {                    
                                                    'Value': {
                                                        'type': {float, np.ndarray},
                                                        'bounds': (0, None),
                                                        # length might not be known in advance: check its consistency only if the 'length' key is found in the input
                                                    },
                                                    'Unit': {
                                                        'dimension': 'currency'
                                                    },   
                                                },                                     
                                                'optional': True,
                                                'description': 'All other variable operating costs.'
                                            },                                                        
                                        },
    }         
                    
}

# Expected resolved output
input_dict_resolved = { 'utilities':{ 
                                'Natural gas': {
                                    'Usage_Value': ureg.Quantity(5.4E9, 'J/kg'),
                                    'Cost_Value': ureg.Quantity(5.555555E-5, 'USD/J'),
                                    'Type': 'natural_gas'
                                },
                                'Electricity': {
                                    'Usage_Value': ureg.Quantity(10.8E9, 'J/kg'),
                                    'Cost_Value': ureg.Quantity(1.388888E-4, 'USD/J'),
                                    'Type': 'electricity'
                                },
                        },
                        'Water Volume':{
                                'Volume':{
                                    'Value': ureg.Quantity(5.E-2, 'meter**3')
                                },
                        },
                        'Number of units': {
                                'Bag number': {
                                    'Value': ureg.Quantity(50, 'dimensionless')
                                },
                        },
                        'Catalyst': {
                                'Lifetime': {
                                    'Value': ureg.Quantity(1.57788E8, 's') # assuming 1 year = 365.25 days
                                },
                        },
                        'Catalyst Separation': {
                                'Filtration cost': {
                                    'Value': ureg.Quantity(1.E2, 'USD/meter**3')
                                },
                        },      
                        'Grid electricity': {
                                'Cost': {
                                    'Value': ureg.Quantity(4.16666667e-8, 'USD/J')
                                },
                        },  
                        'Power Generation': {
                                'Available Power': {
                                    'Value': {
                                        '2025': ureg.Quantity(np.array([1.44e9, 9.0e8, 1.26e9]), 'J'), 
                                        '2024': ureg.Quantity(np.array([1.8e9, 1.26e9, 1.62e9]), 'J')
                                    },
                                },
                                'Stored Power': {
                                    'Value':{
                                        '2025':ureg.Quantity(7.2E8, 'J'),
                                        '2024':ureg.Quantity(9.E8, 'J')
                                     },
                                },                                   
                        },                                    
                        'Power Consumption': {
                                'Any mid key': {
                                    'Value': ureg.Quantity(np.array([3.6E8, 4.32E8, 3.96E8]), 'J') ,
                                    'Type': 'on demand'
                                },   
                                'Another mid key': {
                                    'Value': ureg.Quantity(np.array([1.8E8, 1.44E8, 2.16E8]), 'J') ,
                                    'Type': 'flexible'
                                },   
                        }, 
                        'Pump - Other Variable Operating Cost - Brand A': {
                                'Maintenance': {
                                    'Value': ureg.Quantity(1.25E1, 'USD')
                                },
                                'lubrication': {
                                    'Value': ureg.Quantity(8.2, 'USD')
                                }                                
                        },

                        'Compressor - Other Variable Operating Cost - Brand B': {
                                'lubrication': {
                                    'Value': ureg.Quantity(np.array([1.3, 1.2, 1.1]), 'USD')
                                },   
                                'Electricity': {
                                    'Value': ureg.Quantity(2.2, 'USD')
                                }                                   
                        },                        
                        
}
