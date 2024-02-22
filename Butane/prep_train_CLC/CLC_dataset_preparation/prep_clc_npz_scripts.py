
## Function to extract coordinates from the xyz file into a dictionary 
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
###################################################################################
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
################################################################################
# Function to Parse dump file 

# Define function that parses into diictionary
def parse_lammpstrj(filename):

    import re
    """Parse a LAMMPS trajectory file into a dictionary.

    Parameters
    ----------
    filename : str
        The name of the LAMMPS trajectory file.

    Returns
    -------
    data : dict
        A dictionary containing the data from the LAMMPS trajectory file.

    """
    # Initialize the data dictionary
    data = {}

    # Open the file
    with open(filename, 'r') as f:
        # Read the file line by line
        for line in f:
            # Check if the line starts with 'ITEM: TIMESTEP'
            if line.startswith('ITEM: TIMESTEP'):
                # Extract the timestep number
                timestep = int(next(f))
                data[timestep] = {}
                
            # Check if the line starts with 'ITEM: NUMBER OF ATOMS'
            elif line.startswith('ITEM: NUMBER OF ATOMS'):
                # Extract the number of atoms
                num_atoms = int(next(f))
                data[timestep]['num_atoms'] = num_atoms
                data[timestep]['timestep'] = timestep
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
                
        #     # Sort the atoms by id, which is in the first column
        # for key in data.keys():
        #     data[key]['atoms'].sort(key=lambda x: x[0])
            
        return data

# Use the function to parse the LAMMPS trajectory file
# data = parse_lammpstrj(forces_file)
##########################################################################
## Forces Array

# FUnction to read coordinates from frmaes in xyz dictionary 
def forces_array(data_dict,timestep):
    # Extract xyz coordinates from the dictionary and store them in an array

    #frame = 0
    forces = []
    for row in data_dict[timestep]['atoms']:
        forces.append(row[-3:])
    # Print the array of xyz coordinates
    #print(xyz_coordinates)
    
    return forces