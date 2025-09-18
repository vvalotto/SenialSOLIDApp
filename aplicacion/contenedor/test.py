#function that prints the name of the current working directory and changes the directory to the specified directory in the path
def change_dir(path):
    print("Current working directory: ", os.getcwd())
    os.chdir(path)
    print("Current working directory: ", os.getcwd())
