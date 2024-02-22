import numpy as np 
import matplotlib.pyplot as plt
import lammps_logfile as lmplog
import os
import natsort
import pandas as pd 
from lmp_spc_scripts import read_xyz_traj,xyz_cords_array,lmp_data_subs_coord,change_data_file_name

# data_folder = '.././lmp_Univ2D_spc_5K/'
#data_folder = '../test/'
data_folder = './production_runs/'
# data_folder = './'

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
indices_file = 'index_pcnt_diff.txt'  # Name of the indices file
notfound_count =0

## Check if the lmp_spc_folder exits, if not create it
if not os.path.exists(lmp_spc_folder):
    os.makedirs(lmp_spc_folder)

folders = os.listdir(data_folder)
folders = [f for f in folders if f.startswith("umbrella_") and os.path.isdir(os.path.join(data_folder, f))]
folders = natsort.natsorted(folders)


selected_phi_psi = []

# Loop over indices from selected 
for i in range(len(folders)):
    print(f'\n\nProcessing Umbrella: {i}')

    working_dir = os.path.join(data_folder, f'umbrella_{i}/')
    print(f'Working directory: {working_dir}')

    indices = os.path.join(working_dir, indices_file)

    # Check if the indices file exists in the directory
    if not os.path.isfile(indices):
        print(f"Indices file not found in {working_dir}. Skipping this folder.")
        notfound_count += 1
        continue

    # Get the index from the file
    index = np.genfromtxt(indices)
    print(f'Index with smallest error is {int(index[0])}')
    print(f'The percentage of the error is {index[1].round(2)} %')

    # Load and process colvar_multi*.dat file as a Pandas DataFrame
    colvar_file = os.path.join(working_dir, f'colvar_multi_{i}.dat')  # Replace '*' with the specific filename pattern
    colvar_data = pd.read_csv(colvar_file, delim_whitespace=True)  # Adjust the delimiter if necessary

    # Selecting the row using the obtained index
    selected_row = colvar_data.iloc[int(index[0])] if int(index[0]) < len(colvar_data) else None

    # Get 'phi' and 'psi' columns from the selected row
    phi_psi_values = selected_row[['phi', 'psi']] if selected_row is not None else None
    selected_phi_psi.append(phi_psi_values)


#     # 1. Determine the working directory.
#     working_dir = f'{data_folder}umbrella_{i}/'
#     print(f'Working directory: {working_dir}')
#     print(f'Index with smallest error is {int(indices[i,0])}')
#     print(f'The percentage of the error is {indices[i,1].round(2)} %')

    ## 2. Determine the working xyz file.
    working_xyz_file = working_dir + xyz_traj_file
    print(f'Working xyz file: {working_xyz_file}')

    # Read the coordinates from the xyz file
    xyz_traj_dict = read_xyz_traj(working_xyz_file)

    # Extract the coordinates from the dictionary
    xyz_coordinates = xyz_cords_array(xyz_traj_dict,int(int(index[0])))   #xyz_traj_dict['frames'][indices[i]]

    print(f'\nSubstituting coordinates in data file...')

    # Substitute the coordinates in the lammps data file
    lmp_data_subs_coord(xyz_coordinates,og_data_file,f'{lmp_spc_folder}frame_{i}.data',LOUD=False)
    # REname the filename in the read_data command in the lammps input file
    change_data_file_name(f'{lmp_input_file}',f'frame_{i}.data',LOUD=False)


    #3. Create directory to store lammps data and input files.
    os.makedirs(lmp_spc_folder+f'umbrella_{i}', exist_ok=True)
    print(f'Created directory: {lmp_spc_folder}umbrella_{i}\n\n')

    # move the data file to the folder
    os.system(f'mv {lmp_spc_folder}frame_{i}.data {lmp_spc_folder}/umbrella_{i}/')

    # Copy the input file to the folder
    os.system(f'cp {lmp_input_file} ./plumed.dat {lmp_spc_folder}/umbrella_{i}/')

# Save the selected phi,psi combinations to a file
np.savetxt('selected_phi_psi.txt',np.array(selected_phi_psi))

## PLotting
selected_phi_psi = np.array(selected_phi_psi)

phi = selected_phi_psi[:,0]
psi = selected_phi_psi[:,1]

## Scatter plot of phi,psi combinations

plt.scatter(phi,psi,marker='o',c='r',s=10)
# plt.scatter(extra_phi,extra_psi,marker='o',c='b',s=10)
    
ax = plt.gca()
ax.spines['top'].set_linewidth(2)
ax.spines['right'].set_linewidth(2)
ax.spines['bottom'].set_linewidth(2)
ax.spines['left'].set_linewidth(2)
plt.tick_params(axis='both', which='major', labelsize=14, width=2, length=6)
plt.title(f"{len(folders)-notfound_count} Samples\n",fontsize=18,fontweight="bold")
plt.xlabel("$\phi$ (rad))",fontsize=16,fontweight="bold")
plt.ylabel("$\psi$ (rad)",fontsize=16,fontweight="bold")
plt.tight_layout()

# make x axis ticks go from -pi to pi
# plt.xticks(np.arange(-np.pi, np.pi+1, np.pi/2), [r'$-\pi$', r'$-\pi/2$', r'$0$', r'$\pi/2$', r'$\pi$'])
#plt.savefig(f'phi_psi_scatter.png',dpi=300)
plt.show()