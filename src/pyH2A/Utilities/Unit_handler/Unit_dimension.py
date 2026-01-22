import pint

class UnitDimensionHandler:
    """Handler for unit dimension detection and validation using pint."""
    
    # Constant mapping for dimensionality to dimension
    DIMENSION_MAPPING = {
        "[mass] * [length] ** 2 / [time] ** 2": "energy",
        "[length]": "length",
        "[time]": "time",
        "[current]": "current",
        "[luminosity]": "luminosity",
        "[mass]": "mass",
        "[substance]": "substance",
        "[temperature]": "temperature",
        "[length] ** 3": "volume",
        "dimensionless": "dimensionless"
    }
    
    def __init__(self):
        """Initialize the unit registry."""
        self.ureg = pint.UnitRegistry()
    
    def get_dimension(self, unit_str):
        try:
            unit = self.ureg.Unit(unit_str)
        except Exception:
            raise ValueError(f"'{unit_str}' is not a valid unit. Please provide a valid unit.")

        dimensionality_str = str(unit.dimensionality)
        dimension = self.DIMENSION_MAPPING.get(dimensionality_str)

        if dimension is None:
            raise ValueError(f"'{unit_str}' is not a recognized or supported unit in this context.")

        return dimension
    
