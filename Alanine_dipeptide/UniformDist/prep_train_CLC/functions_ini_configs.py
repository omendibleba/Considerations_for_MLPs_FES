import numpy as np
import matplotlib.pyplot as plt
import os


##################################################################################################
# 1. Function to generate uniformly distributed points in a 2D space.
def generate_centers(bins_1,bins_2, cv1_min_max, cv2_min_max,plot=False):
    # Auto defined inputs
    n_points = bins_1* bins_2

    if n_points <= 0 or bins_1 <= 0 or bins_2 <= 0:
        raise ValueError("Both n and bins must be greater than zero.")

    # Define cvs ranges 
    cv1_range = np.linspace(cv1_min_max[0], cv1_min_max[1], bins_1)
    cv2_range = np.linspace(cv2_min_max[0], cv2_min_max[1], bins_2)

    # Create a grid of points
    cv1_grid, cv2_grid = np.meshgrid(cv1_range, cv2_range)
    cv1_grid = cv1_grid.flatten()
    cv2_grid = cv2_grid.flatten()
    centers = np.array([cv1_grid, cv2_grid])

    if plot:
        plt.figure(figsize=(6, 6))
        plt.scatter(cv1_grid,cv2_grid, c='blue', alpha=0.7)
        plt.xlabel('Cv_1')
        plt.ylabel('Cv_2')
        plt.title(f'{n_points} Uniformly distributed points')
        plt.show()

    return centers

# # Define inputs 
# cv1_bin = 3
# cv1_min_max = [-np.pi, np.pi]
# cv2_bin = 3
# cv2_min_max = [-np.pi, np.pi]

# # Use the function 
# Use the function 
# centers= generate_centers(cv1_bin,cv2_bin,cv1_min_max,cv2_min_max,plot=True)

##################################################################################################

# 2. Funtion to generate inputs for plumed for ADP simulations using th epreviously obtained points.
def generate_plumed_input(centers,bins_1,bins_2):
    """
    centers: Array of centers obtained from the function generate_centers. [cv1, cv2]
    """
    
    # Ensure 
    if len(centers[0]) != bins_1*bins_2:
        raise ValueError("The number of centers is not equal to the total number of bins.")
    
    # Check if tmp folder exists and create it if not. If it exists, delete it and create it again.
    os.makedirs("tmp_plumed_inps",exist_ok=True)

    ## Define inputs for plumed. Specific for this ADP molecule. Selects atoms for phi and psi angles. Add bias of 500 and T = 500 K. 
    for i in range(len(centers[0])):

        with open("tmp_plumed_inps/plumed_"+str(i)+".dat","w") as f:
            print("""
    # vim:ft=plumed
    #MOLINFO STRUCTURE=alanine_dipep.pdb
    phi: TORSION ATOMS=5,7,9,15      #  Values of pshi are correc compareed to the pdb
    psi: TORSION ATOMS=7,9,15,17      # Values of pshi are correc compareed to the pdb 

    bb: RESTRAINT ARG=phi,psi KAPPA=500.0,500.0 AT={},{}
    lw: REWEIGHT_BIAS TEMP=500

    PRINT ARG=phi,psi,bb.bias,lw STRIDE=100 FILE=colvar_multi_{}.dat """.format(centers[0][i],centers[1][i],i),file=f)

# Use the function
# generate_plumed_input(centers,cv1_bin,cv2_bin)
##################################################################################################

# 3. Fucntion to generate Lammps input file for ADP simulations using the previously obtained plumed inputs and centers

def generate_input_files(centers):
    """
    centers: Array of centers obtained from the function generate_centers. [cv1, cv2]
    """
    
    # Check if tmp folder exists and create it if not. If it exists, delete it and create it again.
    if os.path.exists("tmp_inps"):
        os.system("rm -r tmp_inps")
        os.system("mkdir tmp_inps")

    else:
        os.system("mkdir tmp_inps")


    ## Define inputs for plumed. Specific for this ADP molecule. Selects atoms for phi and psi angles. Add bias of 500 and T = 500 K. 
    for i in range(len(centers[0])):

        with open("tmp_inps/input_"+str(i)+".inp","w") as f:
            print(f"""


# Define name of log file 
log adp_clmd_2ns_umb_{str(i)}.log

units			real

neigh_modify    once yes  one  22 page 2200  

atom_style	full
bond_style      harmonic
angle_style     harmonic
dihedral_style  harmonic
pair_style      lj/cut/coul/cut 12.0
pair_modify     mix arithmetic

kspace_style    none 
read_data       example.input   
timestep        1.0

velocity all create 500 3

thermo 1000
thermo_style custom time step etotal ke pe temp press vol

fix pl all plumed plumedfile plumed_{i}.dat outfile plumed.log

fix             1 all nvt temp 500 500 100.0
fix             2 all shake 0.0001 10 0 b 3 5 7 
#fix        	ssages all ssages
dump myDump all custom 1000 forces.dump id type x y z fx fy fz
dump mydumpxyz all xyz 1000 traj_nnip.xyz
special_bonds   amber                               

dump_modify myDump sort id
dump_modify mydumpxyz sort id

#run 1500
run 100000

""".format(i,i,i),file=f)

##################################################################################################
# 4. Functio nto generate production run folders and move everything there.
def generate_production_run(centers):

    os.makedirs("production_runs", exist_ok=True)


    for i in range(len(centers[0])):
        
        # Crete folder for each umbrella
        folder_name = "production_runs/umbrella_" + str(i)
        os.makedirs(folder_name, exist_ok=True)

        # Move lammps input file
        os.system("cp tmp_inps/input_"+str(i)+".inp "+folder_name+"/input_"+str(i)+".inp")

        # Move plumed input file
        os.system("cp tmp_plumed_inps/plumed_"+str(i)+".dat "+folder_name+"/plumed_"+str(i)+".dat")

        # Move data file example.input
        os.system("cp example.input "+folder_name+"/example.input")

#  # Use the function
# generate_folders(centers)
##################################################################################################



