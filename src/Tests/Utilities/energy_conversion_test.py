import pytest
import numpy as np
from scipy import constants as con
from pyH2A.Utilities.energy_conversion import Energy, ureg


class TestEnergyConversion:
    """Test suite for Energy class with Pint-based unit conversions"""

    def test_energy_initialization(self):
        """Test Energy object initialization"""
        energy = Energy(1.5, 'eV')
        assert energy.value == 1.5
        assert energy.unit == 'eV'

    def test_eV_to_J_conversion(self):
        """Test conversion from eV to Joules"""
        energy = Energy(1.0, 'eV')
        expected_J = 1.602176634e-19  # 1 eV in Joules
        assert np.isclose(energy.J, expected_J, rtol=1e-9)

    def test_J_to_eV_conversion(self):
        """Test conversion from Joules to eV"""
        energy = Energy(1.602176634e-19, 'J')
        assert np.isclose(energy.eV, 1.0, rtol=1e-9)

    def test_kWh_to_J_conversion(self):
        """Test conversion from kWh to Joules"""
        energy = Energy(1.0, 'kWh')
        expected_J = 3.6e6  # 1 kWh = 3.6 MJ
        assert np.isclose(energy.J, expected_J, rtol=1e-9)

    def test_J_to_kWh_conversion(self):
        """Test conversion from Joules to kWh"""
        energy = Energy(3.6e6, 'J')
        assert np.isclose(energy.kWh, 1.0, rtol=1e-9)

    def test_kcalmol_conversion(self):
        """Test conversion to kcal/mol"""
        energy = Energy(1.0, 'eV')
        # Convert to kcal/mol using the property
        kcalmol_value = energy.kcalmol
        assert isinstance(kcalmol_value, float)
        assert kcalmol_value > 0

    def test_Jmol_conversion(self):
        """Test conversion to J/mol"""
        energy = Energy(1.0, 'eV')
        # Convert to J/mol using the property
        Jmol_value = energy.Jmol
        expected_Jmol = energy.J * con.Avogadro
        assert np.isclose(Jmol_value, expected_Jmol, rtol=1e-9)

    def test_kJmol_conversion(self):
        """Test conversion to kJ/mol"""
        energy = Energy(1.0, 'eV')
        # Convert to kJ/mol using the property
        kJmol_value = energy.kJmol
        expected_kJmol = (energy.J * con.Avogadro) / 1000
        assert np.isclose(kJmol_value, expected_kJmol, rtol=1e-9)

    def test_nm_wavelength_conversion(self):
        """Test conversion from eV to wavelength in nm"""
        energy = Energy(1.0, 'eV')
        # For 1 eV photon, wavelength = h*c/E
        expected_nm = (con.h * con.c) / (1.602176634e-19) * 1e9
        assert np.isclose(energy.nm, expected_nm, rtol=1e-6)

    def test_hydrogen_production_energy(self):
        """Test energy calculation for hydrogen production (2*1.229 eV)"""
        # Energy for water splitting per molecule
        energy_per_molecule = Energy(2 * 1.229, 'eV')
        
        # Convert to J/mol by multiplying by Avogadro's number
        energy_per_mol_J = energy_per_molecule.J * con.Avogadro
        
        # Should be approximately 237 kJ/mol
        assert np.isclose(energy_per_mol_J / 1000, 237, rtol=0.01)

    def test_solar_insolation_conversion(self):
        """Test typical solar insolation conversion"""
        # Typical solar insolation: 5.5 kWh/m²/day
        insolation = Energy(5.5, 'kWh')
        
        # Convert to Joules
        expected_J = 5.5 * 3.6e6
        assert np.isclose(insolation.J, expected_J, rtol=1e-9)

    def test_to_method_arbitrary_units(self):
        """Test .to() method for arbitrary unit conversions"""
        energy = Energy(100, 'J')
        
        # Test conversion to various units
        assert np.isclose(energy.to('kJ'), 0.1, rtol=1e-9)
        assert np.isclose(energy.to('MJ'), 0.0001, rtol=1e-9)
        assert np.isclose(energy.to('erg'), 1e9, rtol=1e-9)

    def test_repr_method(self):
        """Test string representation of Energy object"""
        energy = Energy(1.5, 'eV')
        assert repr(energy) == "Energy(1.5 eV)"
        
        energy2 = Energy(100, 'kWh')
        assert repr(energy2) == "Energy(100 kWh)"

    def test_roundtrip_conversions(self):
        """Test that converting back and forth preserves values"""
        original_value = 1.23
        
        # eV -> J -> eV
        energy = Energy(original_value, 'eV')
        roundtrip_value = Energy(energy.J, 'J').eV
        assert np.isclose(roundtrip_value, original_value, rtol=1e-9)
        
        # kWh -> J -> kWh
        energy2 = Energy(original_value, 'kWh')
        roundtrip_value2 = Energy(energy2.J, 'J').kWh
        assert np.isclose(roundtrip_value2, original_value, rtol=1e-9)

    def test_all_property_accessors(self):
        """Test that all property accessors return numeric values"""
        energy = Energy(1.0, 'eV')
        
        # All these should return floats without errors
        assert isinstance(energy.J, float)
        assert isinstance(energy.eV, float)
        assert isinstance(energy.nm, float)
        assert isinstance(energy.kcalmol, float)
        assert isinstance(energy.Jmol, float)
        assert isinstance(energy.kWh, float)
        assert isinstance(energy.kJmol, float)

    def test_large_values(self):
        """Test conversions with large energy values"""
        energy = Energy(1e6, 'J')  # 1 MJ
        assert np.isclose(energy.to('MJ'), 1.0, rtol=1e-9)
        assert np.isclose(energy.kWh, 1e6 / 3.6e6, rtol=1e-9)

    def test_small_values(self):
        """Test conversions with small energy values"""
        energy = Energy(1e-20, 'J')
        assert np.isclose(energy.eV, 1e-20 / 1.602176634e-19, rtol=1e-9)

    def test_zero_value(self):
        """Test conversion with zero energy"""
        energy = Energy(0, 'J')
        assert energy.J == 0
        assert energy.eV == 0
        assert energy.kWh == 0

    @pytest.mark.parametrize("value,unit", [
        (1.0, 'eV'),
        (100, 'J'),
        (5.5, 'kWh'),
    ])
    def test_multiple_units(self, value, unit):
        """Parametrized test for multiple unit types"""
        energy = Energy(value, unit)
        assert energy.value == value
        assert energy.unit == unit
        assert energy.J > 0  # All positive energies should give positive Joules


class TestEnergyEdgeCases:
    """Test edge cases and error handling"""

    def test_invalid_unit(self):
        """Test that invalid units raise errors"""
        with pytest.raises(Exception):  # Pint will raise UndefinedUnitError
            Energy(1.0, 'invalid_unit')

    def test_negative_energy(self):
        """Test handling of negative energy values"""
        energy = Energy(-1.0, 'eV')
        assert energy.J < 0


class TestPintIntegration:
    """Test Pint-specific functionality"""

    def test_ureg_availability(self):
        """Test that unit registry is accessible"""
        assert ureg is not None
        # Test that we can create quantities directly
        quantity = 1.0 * ureg('eV')
        assert quantity.magnitude == 1.0

    def test_dimensionality_preservation(self):
        """Test that Pint preserves dimensionality correctly"""
        energy = Energy(1.0, 'eV')
        # Internal quantity should have energy dimensionality
        assert energy._quantity.dimensionality == ureg('J').dimensionality


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v'])
