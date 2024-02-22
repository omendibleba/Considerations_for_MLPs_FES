# Function to read coordinates from xyz file and create a dictionary of the frmaes 
def read_xyz_traj(file_path):
    data_dict = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()

    frames = []
    current_frame = None

    for line in lines:
        line = line.strip()  # Remove leading/trailing whitespaces, if any
        if line.startswith("Atoms. Timestep:"):
            if current_frame is not None:
                frames.append(current_frame)
            current_frame = {
                'timestep': int(line.split()[2]),
                'atoms_data': []
            }
            
     
     
        else:
            atom_info = line.split()
            if len(atom_info) != 4:
                continue  # Skip lines with incorrect data format
            try:
                atom_data = {
                    'atom_type': int(atom_info[0]),
                    'x': float(atom_info[1]),
                    'y': float(atom_info[2]),
                    'z': float(atom_info[3])
                }
            except ValueError:
                continue  # Skip lines with invalid numerical values
            current_frame['atoms_data'].append(atom_data)

    if current_frame is not None:
        frames.append(current_frame)

    data_dict['frames'] = frames
    return data_dict


######################################################################################
# FUnction to read coordinates from frmaes in xyz dictionary 
def xyz_cords_array(data_dict,frame):
    # Extract xyz coordinates from the dictionary and store them in an array

    #frame = 0
    xyz_coordinates = []
    for atom_data in data_dict['frames'][frame]['atoms_data']:
        xyz_coordinates.append([atom_data['x'], atom_data['y'], atom_data['z']])

    # Print the array of xyz coordinates
    #print(xyz_coordinates)
    
    return xyz_coordinates

# # Print the array of xyz coordinates
# xyz_coordinates = xyz_cords_array(xyz_traj_dict,2)
# xyz_coordinates

######################################################################################
# Function to substitute coordinates of the xyz frame in thelammps data file 

def lmp_data_subs_coord(xyz_coords_array,og_data_file,output_file,LOUD=False):
    # og_data_file = './Butane.data'
    # output_file = 'output_file.txt'

    # Read the file contents into a list of lines
    with open(og_data_file, 'r') as file:
        file_contents = file.readlines()

    # Find the starting line number of the Atoms section
    atoms_start_line = None
    for idx, line in enumerate(file_contents):
        if line.strip() == "Atoms":
            atoms_start_line = idx +1
            if LOUD:
                print(f"Atoms section found in the input file.\nStarting line number: {atoms_start_line}")
            break

    if atoms_start_line is not None:
        # Replace the xyz coordinates in the Atoms section
        for i, xyz in enumerate(xyz_coords_array):
            if LOUD:
                print(f"Atom #{i + 1}: {xyz}")
            atom_line = atoms_start_line + i + 1
            if LOUD:
                print(f"Line #{atom_line}: {file_contents[atom_line]}")
            #old_line = file_contents[atom_line]
            
            line = file_contents[atom_line].split()
            #print(line)
            new_xyz_line = f"{line[0]} {line[1]} {line[2]} {line[3]} {xyz[0]:.6f} {xyz[1]:.6f} {xyz[2]:.6f} # {i + 1}\n"
            if LOUD:
                print(f"New line #{atom_line}: {new_xyz_line}")
            #new_line = old_line[:32] + new_xyz_line
            file_contents[atom_line] = new_xyz_line

        # Write the modified contents back to the file
        with open(output_file, 'w') as file:
            file.writelines(file_contents)
        
        if LOUD:
            print(f"Substitution completed successfully. Output file: {output_file}\n")
    else:
        print("Atoms section not found in the input file.")
        
    return 
#################################################################################
## Function to modify the read data file name in the input file 
import re
def change_data_file_name(file_path, new_data_file_name,LOUD=False):
    # Read the contents of the file
    with open(file_path, 'r') as file:
        file_contents = file.read()

    # Define the regex pattern to find the "read_data" line
    pattern = r'read_data\s+([\w.-]+)'

    # Search for the pattern in the file contents
    match = re.search(pattern, file_contents)

    if match:
        # Extract the existing data file name from the matched group
        existing_data_file_name = match.group(1)

        # Replace the existing data file name with the new one
        new_file_contents = file_contents.replace(existing_data_file_name, new_data_file_name)

        # Write the modified contents back to the file
        with open(file_path, 'w') as file:
            file.write(new_file_contents)

        if LOUD:
            print(f"Data file name changed from '{existing_data_file_name}' to '{new_data_file_name}'.")
    else:
        print("Pattern 'read_data' not found or file name not specified in the input file.")
#################################################################################
# PArce force.dump file to extract the forces on each atom

# Define function that parses into diictionary
def parse_lammpstrj(filename):
    import re

    index = 0
    data = {}
    # Open the file
    with open(filename, 'r') as f:
        # Read the file line by line
        for line in f:
            # Check if the line starts with 'ITEM: TIMESTEP'
            if line.startswith('ITEM: TIMESTEP'):
                # Extract the timestep number
                time = int(next(f))
                timestep = int(index)
                print(f"{index}. Timestep={time}")
                index += 1
            if timestep not in data:
                data[timestep] = {}
                data[timestep]['timestep'] = time
                    

            # Check if the line starts with 'ITEM: NUMBER OF ATOMS'
            if line.startswith('ITEM: NUMBER OF ATOMS'):
                # Extract the number of atoms
                num_atoms = int(next(f))
                data[timestep]['num_atoms'] = num_atoms

            # Check if the line starts with 'ITEM: BOX BOUNDS'
            elif line.startswith('ITEM: BOX BOUNDS'):
                # Extract the box bounds
                box_bounds = [float(x) for x in re.findall(r'-?\d+\.\d+', next(f))]
                data[timestep]['box_bounds'] = box_bounds

            # Check if the line starts with 'ITEM: ATOMS'
            elif line.startswith('ITEM: ATOMS'):
                # Initialize the atoms list
                atoms = []
                # Read the rest of the lines in the block
                for _ in range(num_atoms):
                    # Split the line by ' ' and extract the values
                    values = [float(x) for x in next(f).split()]
                    atoms.append(values)
                # Add the atoms list to the data dictionary
                data[timestep]['atoms'] = atoms
                
        return data

# Use the function to parse the LAMMPS trajectory file
# data = parse_lammpstrj(forces_file)