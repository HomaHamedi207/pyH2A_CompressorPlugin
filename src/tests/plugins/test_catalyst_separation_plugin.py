import pytest
from pyH2A.Plugins.Catalyst_Separation_Plugin import Catalyst_Separation_Plugin


class DummyDCF:
    """Minimal DCF object for Catalyst_Separation_Plugin unit testing."""

    def __init__(
        self,
        water_volume_liters,
        filtration_cost_per_m3,
        catalyst_lifetime_years
    ):
        self.inp = {
            "Water Volume": {"Volume (liters)": {"Value": water_volume_liters}},
            "Catalyst": {"Lifetime (years)": {"Value": catalyst_lifetime_years}},
            "Catalyst Separation": {
                "Filtration cost ($/m3)": {"Value": filtration_cost_per_m3}
            },
        }


@pytest.mark.parametrize(
    "water_volume_liters, filtration_cost_per_m3, catalyst_lifetime_years, expected_result",
    [
        (0.0, 50.0, 5.0, 0),  # zero water
        (10000.0, 0.0, 5.0, 0),  # zero filtration cost
        (0.0, 0.0, 5.0, 0),  # both zero
        (1000.0, 50.0, 2.0, 25.0),  # real cases
    ],
)


def test_catalyst_separation_plugin(water_volume_liters, filtration_cost_per_m3, catalyst_lifetime_years, expected_result):
    """Check plugin handles edge and real cases without errors and returns correct annualized costs."""
    dcf = DummyDCF(water_volume_liters, filtration_cost_per_m3, catalyst_lifetime_years)
    plugin = Catalyst_Separation_Plugin(dcf, print_info=False)
    
    assert plugin.yearly_cost == expected_result