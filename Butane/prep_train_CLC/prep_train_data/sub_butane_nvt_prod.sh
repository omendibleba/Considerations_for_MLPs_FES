#!/bin/bash

#$ -pe smp 1     # Specify parallel environment and legal core size
#$ -q long  #hpc@@colon           # Specify queue
#$ -N butane_NVT_prod       # Specify job name

module load cuda/11.0 cudnn/8.0.4 cmake/3.19.2 gsl/gcc/2.7 pytorch/1.13 
#mpich/3.3/gcc/8.5.0

conda activate nequip

#mpirun -np $NSLOTS 
lmp_nequip_plumed -in Butane_SSAGES.in
