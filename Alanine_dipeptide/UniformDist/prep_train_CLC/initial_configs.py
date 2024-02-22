import os
import argparse

parser = argparse.ArgumentParser(description='Generate uniformly distributed points in a 2D space.')
parser.add_argument('cv1_bin', type=int, help='Number of bins for Cv_1')
parser.add_argument('cv1_min', type=float, help='Minimum value of Cv_1')
parser.add_argument('cv1_max', type=float, help='Maximum value of Cv_1')
parser.add_argument('cv2_bin', type=int, help='Number of bins for Cv_2')
parser.add_argument('cv2_min', type=float, help='Minimum value of Cv_2')
parser.add_argument('cv2_max', type=float, help='Maximum value of Cv_2')
parser.add_argument('--plot', action='store_true', help='Flag to plot the points')

args = parser.parse_args()

# 1. Function to generate uniformly distributed points in a 2D space.
from functions_ini_configs import generate_centers

# 2. Funtion to generate inputs for plumed for ADP simulations using th epreviously obtained points.
from functions_ini_configs import generate_plumed_input

# 3. Fucntion to generate Lammps input file for ADP simulations using the previously obtained plumed inputs and centers
from functions_ini_configs import generate_input_files

# 4. Functio nto generate production run folders and move everything there.
from functions_ini_configs import generate_production_run



# Run the script if it is called from the terminal
if __name__ == '__main__':

    # 1. Generate the centers
    centers = generate_centers(
        args.cv1_bin,
        args.cv2_bin,
        [args.cv1_min, args.cv1_max],
        [args.cv2_min, args.cv2_max],
        args.plot
    )
    print("\nInitial configurations generated successfully.\n")

    # 2. Generate the plumed input files
    generate_plumed_input(centers, args.cv1_bin, args.cv2_bin)
    print("Plumed input files generated successfully.\n")

    # 3. Generate the lammps input files
    generate_input_files(centers)
    print("Lammps input files generated successfully.\n")

    # 4. Generate the production run folders
    generate_production_run(centers)
    print("Production run folders generated successfully.\n")

    # remove tmp_inps and tmp_plumed_inps folders
    os.system('rm -rf tmp_inps tmp_plumed_inps')
    
    # Print Exit message
    print("All Done! Thank you!!")