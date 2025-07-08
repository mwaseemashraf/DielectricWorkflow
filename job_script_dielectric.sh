#!/bin/bash

#SBATCH --time=70:00:00   # walltime
#SBATCH --ntasks=2   # number of processor cores (i.e. tasks)
#SBATCH --nodes=1   # number of nodes
#SBATCH --mem-per-cpu=1G   # memory per CPU core
#SBATCH -J "Dielectric"   # job name
#SBATCH --mail-user=waseemashraf1584@gmail.com   # email address
#SBATCH --mail-type=FAIL


# Set the max number of threads to use for programs using OpenMP. Should be <= ppn. Does nothing if the program doesn't use OpenM$
export OMP_NUM_THREADS=$slurm_cpus_on_node to ${slurm_ntasks}

# LOAD MODULES, INSERT CODE, AND RUN YOUR PROGRAMS HERE

module purge
module load gcc/13.2.0-hlknow5 intel-oneapi-mkl/2024.1.0-j45wg6u openmpi/5.0.3-k3xnqaz python #hdf5/1.14.3-oq3jvrl
#module load intel-compilers/2019 intel-mpi/2019 libfabric/1.8
python SolveDielectric.py
