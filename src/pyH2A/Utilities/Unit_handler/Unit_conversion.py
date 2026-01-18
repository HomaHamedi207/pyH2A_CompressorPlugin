import pint
from Unit_dimension import UnitDimensionHandler


class UnitConversionHandler:
    """ Handler for unit conversion using pint. """

    DIMENSION_TO_UNIT_MAPPING = {
        "energy": "J",
        "length": "m",
        "time": "s",
        "current": "A",
        "luminosity": "cd",
        "mass": "g",
        "substance": "mol",
        "temperature": "K",
        "volume": "l"
    }
    
    def __init__(self):
        """ Initialize the unit registry. """
        self.ureg = pint.UnitRegistry()
        self.dimension_handler = UnitDimensionHandler()
    
    def convert(self, value, unit):
        dimension = self.dimension_handler.get_dimension(unit)
        target_unit = self.DIMENSION_TO_UNIT_MAPPING.get(dimension) 
        if target_unit is None:
            raise ValueError(f"No target unit defined for dimension '{dimension}'.")
        quantity = value * self.ureg.Unit(unit)
        converted_quantity = quantity.to(target_unit)
        return converted_quantity


# if __name__ == "__main__":
#     handler = UnitConversionHandler()
#     print(handler.convert(1, 'kWh'))
#     print(handler.convert(100.0, 'cm'))
#     print(handler.convert(60.0, 'min'))