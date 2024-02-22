
# Considerations in the use of ML interaction potentials for free energy calculations

Ref: 

### This repository contains all the input files and required code to obtaine the results discussed in the paper above.

The objective of this research was to train Machhine Learning Potentials (MLPs) using the Allegro package[1], and evaluate their accuracy in predicting the Free Energy Surface (FES) of butane and alanine dipeptide. Additionally, to study the effect that the configurations included in the trainind data, and their representation of the underlying FES, have on the FES prediction accuracy of the models. 

MLPs were trianed usign 10 different distributions for butane and 13 for ADP. These distribution aim to replicate hypotethical scenarios of sampled collective variables (CVs) in a system where the FES is not know.The models were trianed with energues and forces calculated from classical molecular dynamics (CMD) and from single points ab initio calculations (SPC). The trainign configurations were generated uding CMD and the SPC values were calculated for the same configurations. 

The results highlight the extrapolation capabilities of the Allegro model and sheed light into possible limitations for system in which the undelyting FES is not know. They also highlight the challenges of generating a robust training data set for a relatively complex system. In specifi scenarios increasing the amout of trainig data and the representation of configurations in the system FES did not result in a model capable of accuratly recovering the FES of Alanine Dipeptide.


### Usage 

Open the butane or Alanine folder and read the "Full_Tutorial_*.ipynb" notebook.

    - Go over the instructions to generate the butane training and test data distributions with the CLM level of theory using LAMMPS[2].

    - Then calculate the energy and forces of the generated configurations using CP2K[3].

    - Go to the prep_train_CLC and prep_train_SPC folders to train the models. Additionally, evaluate models with test data set.

    - Go to the Unbiased_DPMD folder to find the files to run Deep Potential Molecular dynamics (DPMD) unbiased simulations.
    
    - Go to the Metadynamics_DPMD folder to find the files to run Deep Potential Molecular dynamics (DPMD) metadynamics simulations.


### References
[1] Allegro: https://github.com/mir-group/allegro

[2] LAMMPS: https://github.com/lammps/lammps

[3] CP2K: https://github.com/cp2k/cp2k

