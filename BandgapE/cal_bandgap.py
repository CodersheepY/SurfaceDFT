import os
from ase.io import read, write
from ase.calculators.vasp import Vasp
from ase.dft.bandgap import bandgap

def get_bandgap(cif_file=None, verbose=False):
    """
    Calculate band gap.

    Args:
        cif_file (str): Path to the CIF file of the material.
        verbose (bool): Verbose printing or not.

    Returns:
        badngap (float): Calculated band gap value.
    """

    # Check VASP command environment variable is set

    if os.getenv("ASE_VASP_COMMAND"):
        if verbose:
            print("ASE_VASP_COMMAND is set to:", os.getenv("ASE_VASP_COMMAND"))
    elif os.getenv("VASP_COMMAND"):
        if verbose:
            print("VASP_COMMAND is set to:", os.getenv("VASP_COMMAND"))
    elif os.getenv("VASP_SCRIPT"):
        if verbose:
            print("VASP_SCRIPT is set to:", os.getenv("VASP_SCRIPT"))
    else:
        raise EnvironmentError("One of ASE_VASP_COMMAND, VASP_COMMAND, VASP_SCRIPT should be set. Please ensure it is correctly set in your environment.")

    # Check if VASP_PP_PATH is set
    if not os.getenv("VASP_PP_PATH"):
        raise EnvironmentError("VASP_PP_PATH is not set. Please ensure it is correctly set in your environment.")

    if verbose:
        print("VASP_PP_PATH is set to:", os.getenv("VASP_PP_PATH"))

    # Verify CIF file exists
    if cif_file is None or not os.path.exists(cif_file):
        raise FileNotFoundError(f"The specified CIF file '{cif_file}' does not exist.")

    # Read the structure from the CIF file
    try:
        structure = read(cif_file)
    except Exception as e:
        raise RuntimeError(f"Failed to read structure from CIF file '{cif_file}': {e}")


    # Set up VASP calculator with standard settings

    tmpdir = "tmpdir_bandgap"

    try:
        structure.calc = Vasp(prec="normal",
                              xc="pbe",
                              encut=500,
                              kpts=[8, 8, 8],
                              ismear=0,
                              sigma=0.05,
                              setups='recommended',
                              lwave=True,
                              lcharg=True,
                              nelm=150,
                              algo="fast",
                              ediff=1e-8,
                              npar=4,
                              directory=tmpdir,
                              )
    except Exception as e:
        raise RuntimeError(f"Failed to set up VASP calculator: {e}")

    # Calculate total energy (needed for band structure calculation)
    try:
        energy = structure.get_potential_energy()
    except Exception as e:
        raise RuntimeError(f"Failed to calculate total energy: {e}")

    # Calculate band gap
    try:
        gap, p1, p2 = bandgap(structure.calc, direct=True)
    except Exception as e:
        raise RuntimeError(f"Failed to calculate band gap: {e}")
    
    return gap

if __name__ == "__main__":
    get_bandgap("../BaZrO3.cif")
