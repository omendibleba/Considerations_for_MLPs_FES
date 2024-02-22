# Python script to read CP2K AIMD trajectory and convert to .npz file used to train Allegro MLFF model 
import numpy as np
import matplotlib.pyplot as plt
import argparse
import glob
import re

# Parse command line arguments
parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(description='Convert AIMD of CP2K trajectory to .npz file')

 
parser.add_argument('--input', type=str, default=glob.glob('*-pos-1.xyz'), help='AIMD trajectory file(-pos-1.xyz)')
parser.add_argument('--force', type=str, default=glob.glob('*-frc-1.xyz'), help='AIMD force file(-force-1.xyz)')
parser.add_argument('--colvar', type=str, default=glob.glob('dihedrals.txt'), help='AIMD colvar file(-colvar-1.dat)')
parser.add_argument('--output', type=str, default='aimd', help='Output .npz file')
parser.add_argument('--sample', type=int, default=100, help='Starting frame')
parser.add_argument('--loud', action='store_false', help='Print out more information', default=True)
parser.add_argument('--plot', action='store_true', help='Plot the trajectory', default=False)
args = parser.parse_args()


print("\n\nConvert AIMD of CP2K trajectory to .npz file\n\n")
print("Reading Files...\n")

#Read the file
coord_path = args.input
force_file = args.force
colvar_file = args.colvar
# Check files 
if args.loud:
    try:
        with open(coord_path, 'r') as file:
            coord_lines = file.readlines()
        print(f'Coordinate file read succesfully: {coord_path}')
        
    except:
        print(f'Coordinate file not found: {coord_path}\n\n')

    try:
        with open(force_file, 'r') as file:
            force_lines = file.readlines()
        print(f'Force file read succesfully: {force_file}')
        
    except:
        print(f'Force file not found: {force_file}\n\n')
        
    try:
        colvar_data = np.loadtxt(colvar_file)
        print(f'Colvar file read succesfully: {colvar_file}')
        
    except:
        print(f'Colvar file not found: {colvar_file}\n\n')
        
# Determine coodinates file and forces file have the same number of frames
# Extract the number of frames
num_atoms = int(coord_lines[0].strip())
num_atoms_force = int(force_lines[0].strip())

# Determine the number of frames in the trajectory
num_frames = int(len(coord_lines) / (num_atoms + 2))
num_frames_force = int(len(force_lines) / (num_atoms_force + 2))

# try bloc to check same number of frames and atoms 
try:
    print(f"\n\nTrajectory Details:\n")
    assert num_frames == num_frames_force
    assert num_atoms == num_atoms_force
    print(f'Number of frames: {num_frames}')
    print(f'Number of atoms: {num_atoms}')
    
except:
    print(f'Number of frames in coordinate file: {num_frames}')
    print(f'Number of frames in force file: {num_frames_force}')
    print(f'Number of atoms in coordinate file: {num_atoms}')
    print(f'Number of atoms in force file: {num_atoms_force}')
    print('Number of frames and atoms in coordinate and force files do not match\n\n')
    
# Create dictionary with all the fames 
# Creating dictionary of all coordinates and forces 
print("\n\nCreating dictionary of all coordinates and forces...\n")
data={}

# Iterate over each line in the file
for index, line in enumerate(coord_lines):
    # Use regular expression to check if the line starts with "i ="
    if re.match(r'^\s*i\s*=', line):
        # Process the line as needed
        # Match frame number (i)
        match = re.search(r'i\s*=\s*(\d+)', line)
        if match:
            frame_number = int(match.group(1))
            #print(f'Frame number: {frame_number}')
        else:
            frame_number = None
            
        # Match time
        match = re.search(r'time\s*=\s*([\d.]+)', line)
        if match:
            time = float(match.group(1))
            # Determine if the time at the current frame matches the time at the current frame in the force file
            #print(index)
            #print(f'{force_lines[index].strip().split()[5]} == {time}')

            if time != round(float(force_lines[index].strip().split()[5][:-1]),2):
                print(f"Time in coordinate file ({time}) does not match time in force file ({force_lines[index].strip().split()[5]})")
                print(f"Exiting...")
                #exit()
            else:
                #print(f"Time in coordinate file ({time}) matches time in force file ({force_lines[index].strip().split()[5]})")
                pass
        else:
            time = None
            
        # Match Energy
        match = re.search(r'E\s*=\s*([-\d.]+)', line)
        if match:
            E = float(match.group(1))
            
            if round(E,8) == round(float(force_lines[index].strip().split()[8][:-1]),8):
                pass
            #if args.loud:
                #print(f'Frame number: {frame_number} | Time: {time} | Energy: {E}')
        else:
            #print(f"Energy in coordinate file ({E}) does not match energy in force file ({force_lines[index].strip().split()[8]})")
            #print(f"Exiting...")
            #exit()
            E = None
            
       # Extract coordinates
        coordinates = []
        forces = []
        for j in range(1, num_atoms + 1):
            coordinate_line = coord_lines[index + j]
            force_line = force_lines[index + j]
            
            coordinate_data = coordinate_line.strip().split()
            forces_data = force_line.strip().split()
            
            atom = coordinate_data[0]
            atom_F = forces_data[0]
            if atom != atom_F:
                print(f"Atom in coordinate file ({atom}) does not match atom in force file ({atom_F})")
                print(f"Exiting...")
                #exit()
            x, y, z = map(float, coordinate_data[1:])
            coordinates.append((atom, x, y, z))
            fx, fy, fz = map(float, forces_data[1:])
            forces.append((atom, fx, fy, fz))
            

        #Add the values to the dictionary
        data[frame_number] = {'time': time, 'E': E, 'coordinates': coordinates, 'forces': forces, 'colvar': colvar_data[frame_number]}


if args.loud:
    #print(f"Frame {frame_number+1} of {num_frames} extracted...")
    print(f"[{'=' * int((frame_number+1) / num_frames * 20)}{' ' * (20 - int((frame_number+1) / num_frames * 20))}] {int((frame_number+1) / num_frames * 100)}% Complete", end='\r')
    #Print categories inside each key
    print(f"\n\nPossible values per Keys: {data[0].keys()}")

# Define starting value for frame selection
samples = args.sample
#samples = samples -1
# start = 0
coordinates = []
forces = []
energy = []
diheds = []
atom_types = []

print(f"Creating Array of {samples} samples")

keys = np.array(list(data.keys()))
if args.loud:
    print(f"Total number of frames: {len(keys)}\n")
    print(keys)

random_keys = np.random.choice(keys, samples, replace=False)

if args.loud:
    print(f"\nRandomly selected {samples} frames from {len(keys)} total frames\n")
    print(random_keys)


for frame in random_keys:

    #coordinates.append(data[frame]['coordinates'])
    # Extract tghe last three coliumns of the coordinates
    coordinates.append([x[1:] for x in data[frame]['coordinates']])
    forces.append([x[1:] for x in data[frame]['forces']])
    energy.append(data[frame]['E'])
    diheds.append(data[frame]['colvar'])
        
        
# Get atom types      
atom_types.append([x[0] for x in data[frame]['coordinates']])

atom_types = np.array([6, 1, 1, 1, 6, 1, 1, 6, 1, 1, 6, 1, 1, 1])
        
# COnvert lists to arrays
coordinates = np.array(coordinates)
forces = np.array(forces)
energy = np.array(energy) * 627.509468713739
diheds = np.array(diheds) * 627.509468713739/0.529177208

print(f'\n\nnpz File Information:\n')
print(f'Number of frames: {coordinates.shape[0]}')
print(f"Shape of coordinates array: {coordinates.shape}")
print(f"Shape of forces array: {np.array(forces).shape}")
print(f"Shape of energy array: {np.array(energy).shape}")
print(f"Shape of diheds array: {np.array(diheds).shape}")
print(f"Shape of atom types array: {np.array(atom_types).shape}\n")
print(f"Atom types: {atom_types[0]}")
print(f'Saving data to file :{args.output}.npz\n\n')

# print(energy)
np.savez(f'{args.output}.npz', R=coordinates, F=forces, z=atom_types, E=energy, diheds=diheds)

print(f"All Done! Thank you!!\n\n")
