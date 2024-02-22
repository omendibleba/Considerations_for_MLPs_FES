
import numpy as np
import matplotlib.pyplot as plt
import os 
import subprocess
import natsort
import random 


# Function to find the closest row in the colvar file to the reference array
def find_closest_row(reference, array):
    distances = np.linalg.norm(array - reference, axis=1)
    closest_index = np.argmin(distances)
    
    # Check if the denominator is zero
    norm_reference = np.linalg.norm(reference)
    if norm_reference == 0.0 and distances[closest_index] < 0.01: # Maybe add something to make sure distance is under a cutoff
        percent_difference = float('0.0')  # Handle division by zero case
    else:
        percent_difference = (distances[closest_index] / norm_reference) * 100
    
    return closest_index, percent_difference

#function to give new random number to velocity of lammps input file, and rerun. 
def update_velocity_seed(filename,count):
    
    # Read the file
    with open(filename, 'r') as file:
        lines = file.readlines()
        # Find the line that starts with "velocity"
        for i, line in enumerate(lines):
            if line.startswith('velocity'):
                # Split the line by spaces and extract the values
                values = line.split()[1:]
                new_random_number = str(random.randint(100000, 999999))

                # Assign new random number to the values
                updated_line = f'velocity {" ".join(values[:-1])} {new_random_number}\n'
                lines[i] = updated_line

                # Write the updated content back to the file
                with open(filename, 'w') as file:
                    file.writelines(lines)
                break

    # Add to counter 
    count += 1


## Flag for percent difference under 0.3%
pcnt_diff_flag = False

# Initialize list for index and percent difference
index_list = []
count = 0

# Recal the inital CV from the function 
from functions_ini_configs import generate_centers
# Define inputs 
cv1_bin = 50
cv1_min_max = [-np.pi, np.pi]
cv2_bin = 50
cv2_min_max = [-np.pi, np.pi]

# Use the function 
centers= generate_centers(cv1_bin,cv2_bin,cv1_min_max,cv2_min_max,plot=False)
cv1 = centers[0][0]
cv2 = centers[1][0]
ref_array = np.array([cv1, cv2]).T

# Loop over the files in the production runs folder, and run the lammps simulations
for i, folder in enumerate(natsort.natsorted(os.listdir('production_runs'))):
    if i >= 0:
        while True:
            print(f'Running the lammps simulation for the {i}th folder\n', end='\r')
            print(f'production_runs/{folder}')
            
            os.chdir(f'production_runs/{folder}')
            
            # Input file is the file that ends with .inp
            input_file = [file for file in os.listdir(f'./') if file.endswith('.inp')][0]
            print(input_file + '\n')

            # Run the lammps simulations
            os.system(f'lmp -in {input_file} -log log.txt')
            os.system(f'rm ./bck.*')

            
            
            # Colvar Path
            cv1 = centers[0][i]
            cv2 = centers[1][i]
            ref_array = np.array([cv1, cv2]).T

            # Get the colvar path
            colvar_path = f'colvar_multi_{i}.dat'
            colvar = np.loadtxt(colvar_path)
            time = colvar[:, 0]
            cv1_colvar = colvar[:, 1]
            cv2_colvar = colvar[:, 2]
            colvar_array = np.array([cv1_colvar, cv2_colvar])

            # Find the closest row in the colvar file to the reference array
            closest_index, percent_difference = find_closest_row(ref_array, colvar_array.T)

            # Print the closest index and percent difference
            print(f"{i}. The closest row to {ref_array} is at index {closest_index} \n")
            print(f"{i}. The percent difference is {percent_difference:.2f}% \n")


            # Check if percent_difference is less than 0.3; if so, break out of the while loop
            if percent_difference <= 0.3:
                # Append the index and percent difference to the list
                index_list.append((closest_index, percent_difference))

                # Return to path where loop starts. 
                os.chdir('../../')
                count=0
                break

            else:
                if count < 100:
                    # Run function to give new random number to velocity of lammps input file, and rerun. 
                    update_velocity_seed(input_file,count=count)
                    
                    # Return to path where loop starts. 
                    os.chdir('../../')
                else:
                    # Return to path where loop starts. 
                    os.chdir('../../')
                    break   
                #pass
##############################################################################

    
# Save the list to a file
np.savetxt('index_list.txt',index_list)

plot = True

if plot:

    # # Load the index file
    # index_file = np.loadtxt('./index_list.txt')

    
    # Use the function 
    centers= generate_centers(cv1_bin,cv2_bin,cv1_min_max,cv2_min_max,plot=False)
    cv1 = centers[0][0]
    cv2 = centers[1][0]
    ref_array = np.array([cv1, cv2]).T

    # Load the index file
    index_file = np.loadtxt('./index_list.txt')
    pcnt_difff = index_file[:,1]

    plt.figure(figsize=(6, 6))
    for i in range(len(index_file)):
        cv1 = centers[0][i]
        cv2 = centers[1][i]
        ref_array = np.array([cv1, cv2]).T

        # Get the colvar path

        # Get the colvar path
        colvar_path = f'./production_runs/umbrella_{i}/colvar_multi_{i}.dat'
        colvar = np.loadtxt(colvar_path)
        time = colvar[:,0]
        cv1_colvar = colvar[:,1]
        cv2_colvar = colvar[:,2]
        colvar_array = np.array([cv1_colvar, cv2_colvar])
        closest_index,percent_difference = find_closest_row(ref_array, colvar_array.T)

        # print(f"{i}. The closest row to {ref_array} is at index {closest_index} \n")
        # print(f"{i}. The percent difference is {percent_difference:.2f}% \n")
        # print(f"The closest row is {colvar_array.T[closest_index]}")

        # PLot the CVs
        plt.scatter(centers[0][i],centers[1][i], c='black', alpha=0.7)
        plt.scatter(cv1_colvar[closest_index], cv2_colvar[closest_index], alpha=0.7,label=f'umbrella {i}')
    plt.xlabel('Cv_1')
    plt.ylabel('Cv_2')
    #plt.legend(ncols=5)
    plt.savefig('cv_plot.png',dpi=300)
    plt.show()

    # Plot the percent difference
    plt.figure(figsize=(6, 6))
    plt.plot(pcnt_difff)
    plt.xlabel('Point number',fontsize=14, fontweight='bold')
    plt.ylabel('Percent difference',fontsize=14, fontweight='bold')
    plt.savefig('percent_diff.png',dpi=300)
    plt.show()
