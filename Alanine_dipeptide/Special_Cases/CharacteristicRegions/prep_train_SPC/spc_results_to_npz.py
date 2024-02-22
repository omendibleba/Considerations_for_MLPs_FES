# imports
import numpy as np
import os
import shutil
import re
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(description='Convert AIMD of CP2K trajectory to .npz file')

 
parser.add_argument('--input', type=str, default=None, help='Input npz file containing coordinates to be used for single point calculations)')
parser.add_argument('--samples', type=int, default=500, help='Number of samples to select for single point calculations')
parser.add_argument('--name',type=str, default=None,help='Name of the folders to be created')
parser.add_argument('--output',type=str, default=None,help='Name of the npz dataset to be created')
args = parser.parse_args()


######################################################################
# Functions

# Function to extract energy in atomic units from cp2k output file 
def extract_energy(file_path):
    # Pattern for extracting the energy value from the cp2k output file
    #pattern = r'ENERGY\| Total FORCE_EVAL \( QS \) energy \(a\.u\.\):\s+([-+]?\d*\.\d+|\d+)'
    pattern = r'ENERGY\| Total FORCE_EVAL \( QS \) energy \[a\.u\.\]:\s+([-+]?\d*\.\d+|\d+)'

    with open(file_path, 'r') as file:
        for line in file:
            match = re.search(pattern, line)
            if match:
                numeric_value = float(match.group(1))
                return numeric_value
    return None

# Function to extract atomic forces in atomic units from cp2k output file
def extract_atomic_forces(file_path):
    pattern = r'ATOMIC FORCES in \[a\.u\.\]'
    atomic_forces = []
    atoms = []
    found_section = False

    with open(file_path, 'r') as file:
        for line in file:
            if not found_section:
                if re.search(pattern, line):
                    found_section = True
                    continue
            else:
                if line.startswith('SUM OF ATOMIC FORCES'):
                    break

                values = line.split()
                if len(values) == 6 and values[1].isdigit():  # Line with atom data and a valid atom number
                    atom_number = int(values[1])
                    force_components = [float(values[i]) for i in range(3, 6)]
                    #atomic_forces.append({'Atom': atom_number, 'Force': force_components})
                    atoms.append(atom_number)
                    atomic_forces.append(force_components)

    return atomic_forces,atoms

######################################################################


# To it in a loop to get all the frames
LOUD=True

# Number of frames to extract
n_frames = args.samples - 1

# Load the npz file from CLC as the reference
data = np.load(args.input)
if LOUD:
    print('Files in the npz file: \n')
    print(data.files)


# initialize the arrays
all_energy = []
all_forces = []
all_coords = []
for i in range(0,n_frames+1):
    # Create a copy of the first frame of coordinates 
    if LOUD:
        print('\nFrame: ',i+1,'\n')
    R_0 = data['R'][i].copy()
    if LOUD:
        print('Coordinates:')
        #print(R_0)
        print(f'Shape of coordinates: {R_0.shape}')
        
    # Defien path to log file to extract energies and forces 
    #file_path = f'./but_Boltz_{str(i+1)}/output_traj_{str(i)}.out'
    
    file_path = f'./{args.name}_{str(i+1)}/output_traj.out'
    if LOUD:
        print('\n\nExtracting Energy from file: ')
        print('File path: ',file_path)
        
    # Extract energy
    E_0 = extract_energy(file_path)
    if LOUD:
        print('Energy (a.u): ',E_0)
        
    # Convert energy from au to kcal/mol
    E_0_kcal = E_0 * 627.509468713739
    if LOUD:
        print('Energy (kcal/mol): ',E_0_kcal,'\n\n')
        
    # Extract forces from the same file 
    F_0,atoms = extract_atomic_forces(file_path)
    if LOUD:
        print('Forces (a.u): ')
        print(F_0[0:5])
        #print('Atoms: ',atoms)
        
    # Convert forces from au/bohr to kcal/mol/Angstrom
    F_0_kcal = np.array(F_0) * 627.509468713739 / 0.529177208
    if LOUD:
        print('Forces (kcal/mol/Angstrom): ')
        print(F_0_kcal[0:5])
        
    # Append to lists
    all_energy.append(E_0_kcal)
    all_forces.append(F_0_kcal)
    all_coords.append(R_0)
    

# print the shapes of the arrays
print('\nShape of final arrays stored in the npz file: \n')
print('Energy array shape: ',np.array(all_energy).shape)
print('Forces array shape: ',np.array(all_forces).shape)
print('Coordinates array shape: ',np.array(all_coords).shape)
print('Atomic numbers array shape: ',data['z'].shape)
# Save the array in a .npz file

# Save in npz file
np.savez(f'{args.output}.npz', R=all_coords, F=all_forces, E=all_energy, z=data['z'])
