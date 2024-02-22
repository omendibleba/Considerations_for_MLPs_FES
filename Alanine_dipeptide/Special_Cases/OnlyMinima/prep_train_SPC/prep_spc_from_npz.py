"""""
generate SPC input files for CP2K from a .npz data file
"""""

# imports
import numpy as np
import os
import shutil
import subprocess
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(description='Convert AIMD of CP2K trajectory to .npz file')

 
parser.add_argument('--input', type=str, default=None, help='Input npz file containing coordinates to be used for single point calculations)')
parser.add_argument('--samples', type=int, default=500, help='Number of samples to select for single point calculations')
parser.add_argument('--name',type=str, default=None,help='Name of the folders to be created')
args = parser.parse_args()


print("\n\nCreate folders for single point calculations. \n\n")
print("Reading Files...\n")



# Set LOUD to True to print out more information
LOUD = True

# Define fumber of inputs to be created
n_inputs = args.samples

# Files to be copied into each folder as softlinks 
file_names = file_names = ["BASIS_MOLOPT", "dftd3.dat", "GTH_POTENTIALS", "HFX_BASIS"]


# Load the npz file and print the files 
data = np.load(args.input)
print('The files in this npz file are:\n')
print(data.files)

if LOUD:
    print('\n\n')
    print('Shape of arrays:\n')
    print('Coordinates: ', data['R'].shape)
    print('Energies: ', data['E'].shape)
    print('Forces: ', data['F'].shape)
    print('Types: ', data['z'].shape)
    
    # print the array of types
    print('\nArray of types:\n')
    print(data['z'])

# Modify the array of types for the xyz file 
def replace_values(array):
    for i in range(len(array)):
        if array[i] == 6:
            array[i] = 'C'
        elif array[i] == 1:
            array[i] = 'H'
    return array

# Example usage
original_array = [6, 1, 1, 1, 6, 1, 1, 6, 1, 1, 6, 1, 1, 1]
modified_array = replace_values(original_array)


if LOUD:
    print('\n\n')
    print('Original array of types:\n')
    print(original_array)
    print('\n\n')
    print('Modified array of types:\n')
    print(modified_array)


## Define relevant functions:
# Write an xyz file using the first frame of coordinates
def write_xyz_file(filename, coordinates):
    with open(filename, 'w') as f:
        f.write(f'{len(coordinates)}\n')
        f.write('\n')
        for i, atom in enumerate(coordinates):
            f.write(f'{modified_array[i]}\t')
            f.write(f'{atom[0]}\t{atom[1]}\t{atom[2]}\n')


# Create input for SPC calculation. Based on prep_spcalcs_fiels.py.
def move_xyz_files_to_folders(path,LOUD=True):
    # Get the current directory
    current_dir = path #os.getcwd()
    
    # Get a list of all files in the current directory
    file_list = os.listdir(current_dir)
    
    # Iterate over the files
    for file_name in file_list:
        if file_name.endswith(".xyz"):
            if LOUD:
                print(f'Found file: {file_name}')
                
            # Extract the file name without the extension
            file_name_without_ext = os.path.splitext(file_name)[0]
            
            # Create a new folder with the same name as the file
            new_folder = os.path.join(current_dir, file_name_without_ext)
            if LOUD:
                print(f'Creating new folder: {new_folder}')
            
            # Check if the folder already exists
            if not os.path.exists(new_folder):
                os.makedirs(new_folder)
            
            # Move the file to the new folder
            source_path = os.path.join(current_dir, file_name)
            destination_path = os.path.join(new_folder, file_name)
            shutil.move(source_path, destination_path)
            if LOUD:
                print(f'Moving file: {source_path} to {destination_path}')
    
    print("Files moved into separate folders.")
    

# Fucntion to create soft links of the CP2K potentials into the folders

  
  
def create_soft_links(target_dir, file_names,stsr_with='test'):
    # Ensure the destination folder exists
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Iterate through the file list and create symbolic links
    for file_name in file_names:
        source_path = os.path.abspath(file_name)
        destination_path = os.path.join(target_dir, os.path.basename(file_name))
        
        # Check if the file already exists in the destination folder
        if os.path.exists(destination_path):
            print(f"Symbolic link for '{file_name}' already exists in '{target_dir}'. Skipping.")
        else:
            os.symlink(source_path, destination_path)
            print(f"Symbolic link created for '{file_name}' in '{target_dir}'.")


    print(f'Soft links created for {target_dir}')
    
    
# TEst the function to create the input file for SPC calculation


def generate_inputs_spc(folder_path):
    # Iterate over all subdirectories inside the folder
    for subdir in os.listdir(folder_path):
        subfolder_path = os.path.join(folder_path, subdir)
        
        # Check if it's a directory
        if os.path.isdir(subfolder_path):
            # Look for .xyz files in the subdirectory
            for file_name in os.listdir(subfolder_path):
                if file_name.endswith(".xyz"):
                    xyz_file_path = os.path.join(subfolder_path, file_name)
                    
                    # Read the content of traj_0.inp as template
                    template_file_path = "traj_0.inp" #os.path.join(folder_path, "traj_0.inp")
                    with open(template_file_path, 'r') as template_file:
                        template_lines = template_file.readlines()
                    
                    # Find and replace the COORD_FILE_NAME value
                    modified_lines = []
                    for line in template_lines:
                        if "COORD_FILE_NAME" in line:
                            modified_lines.append(f"        COORD_FILE_NAME {file_name}\n")
                        else:
                            modified_lines.append(line)
                    
                    # Create a copy of traj_0.inp with modified COORD_FILE_NAME
                    modified_inp_file_path = os.path.join(subfolder_path, "traj_0_modified.inp")
                    with open(modified_inp_file_path, 'w') as modified_inp_file:
                        modified_inp_file.writelines(modified_lines)
                    
                    #print(f"Replaced COORD_FILE_NAME in traj_0.inp with {file_name} and saved as traj_0_modified.inp in {subfolder_path}")
    print("Inputs created for ", folder_path)
    



    
####################################################################################################################    
# Loop over the frames in the .npz file to create input foders 

for i in range(n_inputs):
    print(f'\n\nCreating input {i+1} of {n_inputs}\n')
    # Create copy of the array of coordinates
    R_0 = data['R'][i].copy()
    #print(R_0)
    
    # Wirte the xyz file 
    write_xyz_file(f'{args.name}_{i+1}.xyz', R_0)
    
    #Move the file to a folder
    move_xyz_files_to_folders(os.getcwd())
    
    # Create soft links of the CP2K potentials into the folders
    create_soft_links(f'{args.name}_{i+1}', file_names)

#     # Write submission files 
#     with open("sub_umb_"+str(i+1)+".sh","w") as f:
#         print(f"""#!/bin/bash

# #$ -pe smp 12         # Specify parallel environment and legal core size
# #$ -q long            # Run on the GPU cluster 
# #$ -N SPCBoltz{str(i+1)}       # Specify job name

# module load cp2k
    
# mpirun -np $NSLOTS cp2k.popt -o output_traj_{i}.out -i traj_0_modified.inp""".format(i,i),file=f)

#     # COpy submission file to each folder
#     subprocess.run(['mv', f'sub_umb_{i+1}.sh', f'but_Boltz_{i+1}'])
    
    # Generate the input files for SPC calculation
generate_inputs_spc(f'./')

print(f'Files generated sucessfully.')
