import pytest
import numpy as np
from pyH2A.Plugins.Catalyst_Separation_Plugin import Catalyst_Separation_Plugin

class DummyDCF:
    """Minimal DCF object for Catalyst_Separation_Plugin unit testing."""
    def __init__(self, water_volume_liters=10000.0, filtration_cost_per_m3=50.0, catalyst_lifetime_years=5.0):
        self.inp = {
            'Water Volume': {'Volume (liters)': {'Value': water_volume_liters}},  
            'Catalyst': {'Lifetime (years)': {'Value': catalyst_lifetime_years}} ,
            'Catalyst Separation': {'Filtration cost ($/m3)': {'Value': filtration_cost_per_m3}},
        }

@pytest.fixture(scope="module")
def plugin_run():
    """Fixture that runs the plugin once and returns both the DCF and plugin's yearly cost."""
    dcf = DummyDCF()
    plugin = Catalyst_Separation_Plugin(dcf, print_info=False)
    # Return both DCF and the plugin's yearly cost
    return dcf, plugin.yearly_cost, plugin.yearly_filtration_volume_m3

# def get_yearly_cost(dcf: DummyDCF) -> float:
#     """Safely get the yearly catalyst separation cost from DCF."""
#     try:
#         return dcf.inp['Other Variable Operating Cost - Catalyst Separation']['Catalyst Separation (yearly cost)']['Value']
#     except KeyError:
#         raise KeyError("Yearly catalyst separation cost not found. Did the plugin run?")

def test_catalyst_separation_yearly_cost(plugin_run):
    """Test the yearly catalyst separation cost matches expected annualized value."""
    dcf, actual_yearly_cost, actual_volume_m3 = plugin_run

    #water_volume_m3 = dcf.inp['Water Volume']['Volume (liters)']['Value'] / 1000.0
    #filtration_cost = dcf.inp['Catalyst Separation']['Filtration cost ($/m3)']['Value']
    #catalyst_lifetime = dcf.inp['Catalyst']['Lifetime (years)']['Value']

    # Annualized cost over catalyst lifetime
    #expected_yearly_cost = (water_volume_m3 * filtration_cost) / catalyst_lifetime
    
    expected_yearly_cost =  ((10000 / 1000) * 50) / 5

    assert actual_yearly_cost == pytest.approx(expected_yearly_cost), (
        f"Expected yearly catalyst separation cost {expected_yearly_cost} $ "
        f"but got {actual_yearly_cost}"
    )

def test_catalyst_separation_yearly_volume(plugin_run):
    """Test the annualized filtration volume in m3."""
    dcf, actual_yearly_cost, actual_volume_m3 = plugin_run
    
    """
    expected_volume_m3 = dcf.inp['Water Volume']['Volume (liters)']['Value'] / 1000.0 / \
                         dcf.inp['Catalyst']['Lifetime (years)']['Value']
    """
    
    expected_volume_m3 = (10000 / 1000) / 5
    assert actual_volume_m3 == pytest.approx(expected_volume_m3), (
        f"Expected yearly filtration volume {expected_volume_m3} m3, but got {actual_volume_m3} m3"
    )

def test_catalyst_separation_full_plugin_output(plugin_run):
    """Test multi-year cost array matches expected behavior over catalyst lifetime."""
    dcf, actual_yearly_cost, actual_volume_m3 = plugin_run
    
    #filtration_cost = dcf.inp['Catalyst Separation']['Filtration cost ($/m3)']['Value']
    #water_volume_m3 = dcf.inp['Water Volume']['Volume (liters)']['Value'] / 1000.0
    #catalyst_lifetime = dcf.inp['Catalyst']['Lifetime (years)']['Value']

    #expected_yearly_cost = (water_volume_m3 * filtration_cost) / catalyst_lifetime
    #expected_cost_array = np.full(int(np.ceil(catalyst_lifetime)), expected_yearly_cost)
    
    expected_yearly_cost =  ((10000 / 1000) * 50) / 5
    expected_cost_array = np.full(int(np.ceil(5)), expected_yearly_cost)

    actual_cost_array = np.full(int(np.ceil(5)), actual_yearly_cost)

    np.testing.assert_allclose(actual_cost_array, expected_cost_array,
                               err_msg=f"Catalyst separation yearly costs mismatch over {5} years.")

@pytest.mark.parametrize(
    "water_volume_liters, filtration_cost_per_m3, catalyst_lifetime_years",
    [
        (0.0, 50.0, 5.0),       # zero water
        (10000.0, 0.0, 5.0),    # zero filtration cost
        (0.0, 0.0, 5.0),        # both zero
    ]
)

def test_edge_cases(water_volume_liters, filtration_cost_per_m3, catalyst_lifetime_years):
    """Check plugin handles edge cases without errors and returns correct annualized costs."""
    dcf = DummyDCF(water_volume_liters, filtration_cost_per_m3, catalyst_lifetime_years)
    plugin = Catalyst_Separation_Plugin(dcf, print_info=False)

    expected_yearly_cost = (water_volume_liters / 1000.0 * filtration_cost_per_m3) / catalyst_lifetime_years

    assert plugin.yearly_cost == pytest.approx(expected_yearly_cost), (
        f"Edge case failed: water {water_volume_liters} L, filtration cost {filtration_cost_per_m3} $/m3, "
        f"lifetime {catalyst_lifetime_years} years. Expected {expected_yearly_cost}, got {plugin.yearly_cost}"
    )
