import os

working_dir = "/Users/lynevans/Documents/Ge/Ge Capital/GEC-NOLA-CTC/Udacity/prank"
def rename_files():
    file_list = os.listdir("/Users/lynevans/Documents/Ge/Ge Capital/GEC-NOLA-CTC/Udacity/prank")
    print(file_list)


    os.chdir(working_dir)
    for file_name in file_list:
       print("Old name: " + file_name)
       os.rename(file_name, file_name.translate(None, "0123456789"))
       print("New name: " + file_name.translate(None, "0123456789")))


rename_files()
