"""
This script gives some examples for using the openLCA matrix export in Python.
You need to have NumPy and SciPy installed, e.g. via pip

  pip install -U numpy scipy

Note that all calculations in these examples are currently done with dense
matrices. Sparse matrices are converted to a dense format in these calculations.
If you want to use faster calculations for sparse matrices checkout the direct
and iterative solvers from the SciPy package:

  https://docs.scipy.org/doc/scipy/reference/sparse.linalg.html
"""

import numpy as np
from pyH2A import Discounted_Cash_Flow
from pyH2A.LCA.LCA_lib import ExportFolder, Matrix, solve 
from pyH2A.Utilities.input_modification import process_table
import pprint as pp

class LCA:
    """
        Wrapper class for performing Life Cycle Assessment (LCA) calculations
        using openLCA matrix exports within the pyH2A framework.

        The class constructs a scaling vector from pyH2A input tables,
        performs matrix-based LCA calculations, and stores impact results
        in a structured format.

        Parameters
        ----------
        matrix_folder : str
            Path to the openLCA matrix export folder containing the
            technosphere (A), intervention (B), characterization (C),
            and demand (f) matrices.
        dcf : pyH2A.Discounted_Cash_Flow
            pyH2A Discounted_Cash_Flow object containing model input tables,
            including LCA-related scaling information.

        Attributes
        ----------
        folder : ExportFolder
            Loaded openLCA export folder.
        tech_index_dict : dict
            Dictionary mapping process UUIDs to TechEntry objects.
        A : ndarray or scipy.sparse matrix
            Technosphere matrix.
        B : ndarray or scipy.sparse matrix
            Intervention (biosphere) matrix.
        C : ndarray or scipy.sparse matrix
            Characterization matrix.
        f : ndarray
            Demand vector.
        scaling_vector : ndarray
            Vector used to scale LCA processes based on pyH2A inputs.
        lca_results : dict
            Dictionary of LCA results with impact names as keys and
            dictionaries containing values and units.

        Notes
        -----
        This implementation assumes that all processes required by the
        openLCA model are explicitly scaled through pyH2A input tables.
        An error is raised if the scaling vector is incomplete.
    """
      
    def __init__(self, matrix_folder: str, dcf: Discounted_Cash_Flow):
        """
            Initializes the LCA object and performs the LCA calculation.

            Parameters
            ----------
            matrix_folder : str
                Path to the openLCA matrix export folder.
            dcf : pyH2A.Discounted_Cash_Flow
                pyH2A Discounted_Cash_Flow object containing model inputs
                used to construct the scaling vector.
        """

        self.folder = self.import_folder(matrix_folder)
        self.tech_index_dict = self.folder.tech_index()
        self.A, self.B, self.C, self.f = self.load_matrices()
        self.build_scaling_vector(dcf)

        self.perform_LCA()
        

    def import_folder(self, folder: str) -> ExportFolder:
        """
            Imports an openLCA matrix export folder and verifies that
            impact assessment data are available.

            Parameters
            ----------
            folder : str
                Path to the openLCA export folder.

            Returns
            -------
            ExportFolder
                Loaded openLCA export folder.

            Raises
            ------
            RuntimeError
                If the export folder does not contain impact data.
        """

        export_folder = ExportFolder(folder)

        if not export_folder.has_impacts():
            print('error: no impacts in your export')
            return
        else:
            return export_folder

    def load_matrices(self):
        """
            Loads the technosphere, intervention, characterization,
            and demand matrices from the openLCA export folder.

            Returns
            -------
            A : ndarray or scipy.sparse matrix
                Technosphere matrix.
            B : ndarray or scipy.sparse matrix
                Intervention matrix.
            C : ndarray or scipy.sparse matrix
                Characterization matrix.
            f : ndarray
                Demand vector.
        """

        A = self.folder.load(Matrix.A)
        B = self.folder.load(Matrix.B)
        C = self.folder.load(Matrix.C)
        f = self.folder.load(Matrix.f)

        return A, B, C, f
    
    def build_scaling_vector(self, dcf):
        """
            Builds the scaling vector used for the LCA calculation.

            The scaling vector is populated using pyH2A input tables
            associated with LCA processes. Unit consistency is enforced
            during population.

            Parameters
            ----------
            dcf : pyH2A.Discounted_Cash_Flow
                pyH2A Discounted_Cash_Flow object containing LCA-related
                input tables and production values.

            Raises
            ------
            ValueError
                If any entries in the scaling vector remain zero after
                processing all LCA input tables.

            Notes
            -----
            The scaling vector must be fully populated to ensure
            correct LCA results. Missing values indicate incomplete
            or inconsistent pyH2A input definitions.
        """

        table_group = 'LCA'
        self.scaling_vector = np.zeros_like(self.f)

        total_H2_production = np.sum(dcf.inp['Technical Operating Parameters and Specifications']['Output per Year at Gate']['Value'])
        self.scaling_vector[0] = total_H2_production

        for key in dcf.inp:
            if table_group in key:
                process_table(dcf.inp, key, 'Value')
                process_LCA_table(self.scaling_vector, dcf.inp[key], self.tech_index_dict)

        ### Adding check that scaling vector is completely populated with data (no zeros).
        if np.any(self.scaling_vector == 0):
            zero_indices = np.where(self.scaling_vector == 0)[0]
            missing_processes = [k for k, v in self.tech_index_dict.items() if v.index in zero_indices]
            raise ValueError(f"Scaling vector has unpopulated entries at indices {zero_indices}. Missing processes: {missing_processes}")

    def perform_LCA(self):
        """
            Performs the Life Cycle Impact Assessment (LCIA) calculation.

            The method computes intermediate flows and final impact
            results using the intervention and characterization matrices.
            Results are stored in the class instance.

            Notes
            -----
            Final results are stored in the attribute `lca_results`
            as a dictionary mapping impact names to values and units.
        """

        g = self.B @ self.scaling_vector
        h = self.C @ g

        # Adding real data export into LCA class instance instead of printing results
        self.lca_results = {}
        for i in self.folder.impact_index():
            self.lca_results[i.impact_name] = {
                'value': h[i.index],
                'unit': i.impact_unit
            }

        for impact_name, data in self.lca_results.items():
                print(f"{impact_name} , {data['value']:.5f} , {data['unit']}")            

def process_LCA_table(scaling_vector : np.ndarray, input_table : dict, tech_index_dict : dict):
    """
        Processes a pyH2A LCA input table and populates the scaling vector.

        The function assigns values to the scaling vector based on
        process UUIDs and performs unit checks and conversions to
        ensure consistency with the openLCA model.

        Parameters
        ----------
        scaling_vector : numpy.ndarray
            Vector used to scale LCA processes.
        input_table : dict
            pyH2A-formatted input table containing process UUIDs,
            values, and units.
        tech_index_dict : dict
            Dictionary mapping process UUIDs to TechEntry objects.

        Notes
        -----
        Unit conversion is applied where supported. Unknown units
        are assumed to be consistent with the openLCA export.
    """

    # conversion factors to consistent units
    unit_conversion = {
        'ton': 1000,   # tons -> kg
        'kg': 1,
        'kWh': 3.6,    # kWh -> MJ
        'MJ': 1
    }

    for key in input_table:
        uuid = input_table[key]['UUID']
        value = input_table[key]['Value']
        unit = input_table[key].get('Unit', None)  # Expect 'Unit' field in table

        # Convert to consistent unit if unit is known
        if unit in unit_conversion:
            value_converted = value * unit_conversion[unit]
        else:
            value_converted = value  # Assume already consistent if unit unknown


        tech_index = tech_index_dict[uuid].index
        scaling_vector[tech_index] = value_converted
        

def lcia_example():
    """
        Example function demonstrating how to perform an LCIA
        calculation using an openLCA matrix export.

        Notes
        -----
        This function is intended for demonstration and testing
        purposes and prints impact assessment results to stdout.
    """

    folder = ExportFolder('pyH2A/LCA/LCA_Test_Data')

    if not folder.has_impacts():
        print('error: no impacts in your export')
        return
    

    tech_index = folder.tech_index()
    pp.pprint(tech_index['0b61b77e-1364-404e-a16e-fb473dc1486a'].process_name)

    #pp.pprint(vars(tech_index[0]))

    # load the matrices
    A = folder.load(Matrix.A)
    B = folder.load(Matrix.B)
    C = folder.load(Matrix.C)
    f = folder.load(Matrix.f)


    # calculate the LCIA result
    scaling = solve(A, f)
    g = B @ scaling
    print(f)
    h = C @ g

    for i in folder.impact_index():
        print('%s , %.5f , %s' % (i.impact_name, h[i.index], i.impact_unit))


if __name__ == '__main__':
    lcia_example()
