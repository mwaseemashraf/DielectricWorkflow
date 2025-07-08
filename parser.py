import pymatgen
from pymatgen.io.vasp.outputs import Outcar, Vasprun
# Activate the environment
env.activate("")

vr = Vasprun('vasprun.xml')
outcar = Outcar('OUTCAR')
#print(vr.as_dict())
print(outcar.as_dict())
