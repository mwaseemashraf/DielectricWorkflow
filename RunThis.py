import os
import shutil
import numpy as np
import pandas as pd
from datetime import datetime
from itertools import product
from toolbox import up, down, filechk, POTCAR_compiler, add_or_update_incar_tag, make_supercell_matrix , get_material_data
from toolbox import submit_sbatch_job, submit_sbatch_job_with_dependency, create_shell_directory, get_unique_supercell_triplets, kpoints_for_supercell
from pymatgen.io.vasp.inputs import Kpoints, Incar
from pymatgen.io.vasp.sets import MPRelaxSet
from pymatgen.ext.matproj import MPRester
from pymatgen.transformations.standard_transformations import SupercellTransformation

root_dir = os.getcwd()
shell_dir = create_shell_directory()
batch_dir = os.getcwd()
#down(shell_dir)
# --- Setup parameters ---
ID = "mp-2574"
triplets, replace_limits, molpercent = get_material_data(ID)
supercell_triplets = triplets
triplet = [1, 1, 1]
kmesh = kpoints_for_supercell(triplet, base_mesh=8)
kmesh=[8,8,8]
supercell_size = make_supercell_matrix(1, 1, 1)
supercell_str = f"{1}x{1}x{1}"
kmesh_str = f"{kmesh[0]}x{kmesh[1]}x{kmesh[2]}"
atom_to_replace, new_element = 'Zr', 'Y'
#supercell_str = f"{supercell_size[0][0]}x{supercell_size[1][1]}x{supercell_size[2][2]}"
filename = os.path.join(shell_dir, f"{ID}_{supercell_str}_{kmesh_str}_Y_in_Zr_test")
api_key = "2Kph2GG3x9ryu4tplcEN4VVKzdV4ilKc"
# --- File setup ---
os.makedirs(filename, exist_ok=True)
for f in ['job_script.sh', 'INCAR_d', 'parser.py', 'SolveDielectric.py' , 'job_script_dielectric.sh', 'toolbox.py']:
    shutil.copy(os.path.join(root_dir, f), filename)  # Go up two levels from filename to access original file
down(filename)

# --- Get and modify structure ---
with MPRester(api_key) as mpr:
    structure = mpr.get_structure_by_material_id(ID)
    supercell_structure = SupercellTransformation(supercell_size).apply_transformation(structure)

replaced_structure = supercell_structure.copy()
replaced = 0
for i, site in enumerate(replaced_structure.sites):
    if site.specie.symbol == atom_to_replace and replaced < 1:
        replaced_structure[i] = new_element
        replaced += 1
# --- Save run info ---
#pd.DataFrame({'ID': ID, 'Supercell': [supercell_size]}).to_csv(
#    f"{ID}-{supercell_size[0][0]}{supercell_size[1][1]}{supercell_size[2][2]}-{replace_limit}.csv", index=False
#)

# --- Create and write VASP input files ---
vis = MPRelaxSet(replaced_structure, force_gamma=True)
os.makedirs("Optimize", exist_ok=True)
shutil.copy("job_script.sh", "Optimize")
down("Optimize")
kpoints = Kpoints.monkhorst_automatic(kpts=kmesh)
vis = MPRelaxSet(replaced_structure, force_gamma=True, user_kpoints_settings=kpoints)
for name, data in zip(["INCAR", "KPOINTS", "POSCAR"], [vis.incar, vis.kpoints, vis.poscar]):
    with open(name, 'w') as f:
        f.write(str(data))
open("POTCAR", 'w').close()
POTCAR_compiler(vis.potcar_symbols)

# --- Edit INCAR tags ---
magmom_list = [0.0] * len(replaced_structure)
magmom_str = ' '.join(map(str, magmom_list))
incar_tags = {
    'EDIFFG': '-0.01',
    'EDIFF': '1e-8',
    'ISMEAR': '0',
    'ALGO': 'NORMAL',
    'MAGMOM': magmom_str
}
for tag, value in incar_tags.items():
    add_or_update_incar_tag('INCAR', tag, value)
# --- Submit job ---
#print(len(replaced_structure))
jobID = submit_sbatch_job("job_script.sh")
up("Optimize")

# --- Dielectric job prep ---
dielectric_dir = "Dielectric"
os.makedirs(dielectric_dir, exist_ok=True)
for f in ["INCAR_d", "parser.py", "job_script_dielectric.sh", 'SolveDielectric.py' , "job_script.sh", "toolbox.py"]:
    shutil.copy(os.path.join(root_dir, f), dielectric_dir)
down(dielectric_dir)
add_or_update_incar_tag('INCAR_d', 'MAGMOM', magmom_str)
num_kpoints = np.prod(kmesh)
ismeartag = "0"  # safe Gaussian smearing
add_or_update_incar_tag('INCAR_d', 'ISMEAR', ismeartag)
submit_sbatch_job_with_dependency("job_script_dielectric.sh", jobID)

# --- Final sync ---
os.chdir(batch_dir)
