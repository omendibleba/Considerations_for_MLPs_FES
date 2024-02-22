import numpy as np 
import matplotlib.pyplot as plt
import lammps_logfile as lmplog
import os
import glob
import plumed
from lmp_spc_scripts import read_xyz_traj,xyz_cords_array,lmp_data_subs_coord,change_data_file_name

import warnings
warnings.filterwarnings("ignore")


# data_folder = '.././lmp_Univ2D_spc_5K/'
#data_folder = '../test/'
data_folder = 'production_runs/'

# workig_folder = 'umbrella_'
log_file = 'adp_clmd_2ns_umb_' #'log.lammps'
forces_file = 'forces.dump'
xyz_traj_file = 'traj_nnip.xyz'

lmp_spc_folder = './lmp_spc_2500Frames/' # Folder were new data files will be saved. LAMMPS spc
workig_folder = 'umbrella_'
og_data_file = './example.input'
lmp_input_file = './input_0.inp'

verbose =True
# Load the indices per umrbrlal used to generate the 2D histogram

#indices = np.loadtxt('./index_list.txt')
# indices = np.loadtxt('./Selected_indices.txt')

indices_file = 'index_pcnt_diff.txt'
# indices[:5,0]

# Use glob to determine the number of folders that start with umbrella_*

# Get the current directory
current_directory = os.getcwd()

# Use glob to find all folders that start with 'umbrella_'
folders = glob.glob(f'{current_directory}/{data_folder}umbrella_*')

# Print the number of folders
#print(len(folders))

found_count = 0
notfound_count = 0
selected_phi_psi = []


for i in range(len(folders)):
    print(f'\n\nProcessing Umbrella: {i}')

    working_dir = os.path.join(data_folder, f'umbrella_{i}/')
    print(f'Working directory: {working_dir}')

    indices = os.path.join(working_dir, indices_file)

    found_count += 1
    
    # Check if the indices file exists in the directory
    if not os.path.isfile(indices):
        print(f"Indices file not found in {working_dir}. Skipping this folder.")
        notfound_count += 1
        continue

    #print(f'Indices Found: {indices}')

    # Get the index from the file 
    index = np.genfromtxt(indices)
    #print(f'Index with smallest error is {int(index[0])}')
    #print(f'The percentage of the error is {index[1].round(2)} %')

    # Load and process colvar_multi*.dat file
    colvar_file = os.path.join(working_dir, f'colvar_multi_{i}.dat')  # Replace '*' with the specific filename pattern
    colvar_data = plumed.read_as_pandas(colvar_file)

    # Selecting the row using the obtained index
    selected_row = colvar_data.iloc[int(index[0])] if int(index[0]) < len(colvar_data) else None

    # Get 'phi' and 'psi' columns from the selected row
    phi_psi_values = selected_row[['phi', 'psi']] if selected_row is not None else None
    selected_phi_psi.append(phi_psi_values)

#selected_phi_psi = np.array(selected_phi_psi)
#selected_phi_psi

# save the phi and psi values to a file
np.savetxt('selected_phi_psi.txt', selected_phi_psi)

# save as npy file
np.save('selected_phi_psi.npy', selected_phi_psi)