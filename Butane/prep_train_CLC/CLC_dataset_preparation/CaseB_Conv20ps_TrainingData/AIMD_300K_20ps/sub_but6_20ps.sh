#!/bin/bash


#$ -pe smp 8
#$ -q hpc@@colon
#$ -N Butane_solv_aimd 

module load cp2k
mpirun -n $NSLOTS cp2k.popt -i butane_solv_aimd_40K.inp  -o but6_300K_20ps.log
