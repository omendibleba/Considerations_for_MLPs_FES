import os
from multiprocessing import Pool

def run_command(folder):
    # Get the current working directory
    current_directory = os.getcwd()

    # Change to the umbrella folder
    os.chdir(folder)

    # Run the command inside the umbrella folder
    command = "lmp -in Butane.in"
    os.system(command)

    # Change back to the original directory
    os.chdir(current_directory)

if __name__ == "__main__":
    # Get a list of folders starting with 'umbrella_'
    umbrella_folders = [folder for folder in os.listdir() if folder.startswith('umbrella_') and os.path.isdir(folder)]

    # Define the number of processes for the pool (you can adjust this number)
    num_processes = 4  # Change this number as needed

    # Create a multiprocessing Pool
    with Pool(num_processes) as pool:
        # Map the folders to the run_command function
        pool.map(run_command, umbrella_folders)
