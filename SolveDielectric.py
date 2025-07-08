import os
from toolbox import up
from toolbox import down
from toolbox import submit_sbatch_job, submit_sbatch_job_with_dependency
from toolbox import add_or_update_incar_tag


up("Dielectric")
#down("Optimize")
os.system("cp Optimize/POTCAR ./Dielectric")
os.system("cp Optimize/KPOINTS ./Dielectric")
os.system("cp Optimize/CONTCAR ./Dielectric")
os.system("cp Optimize/INCAR_d ./Dielectric")
down("Dielectric")
os.system("cp INCAR_d INCAR")
os.system("cp CONTCAR POSCAR")
#add_or_update_incar_tag('./INCAR','MAGMOM','12*-0.0')
submit_sbatch_job("job_script.sh")
up("Dielectric")