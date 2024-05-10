import os 
from PIL import Image
from flask import url_for,current_app

def add_profile_pic(pic_upload,username):
    """Assigns the file input from user to a unique filename, sets it to thumbnail size, returns the storage name
    
    Args: 
    pic_upload - uploaded picture by user
    username - the user's username
    
    Returns: the name the file is stored as
    """
    filename = pic_upload.filename
    ext_type = filename.split('.')[-1] #Checks if the file type is png or jpg
    storage_filename = str(username) + '.' +ext_type #Converts uploaded image to a unique filename
    filepath = os.path.join(current_app.root_path,'static\profile_pics', storage_filename) #stores the name of file in static
    output_size = (800,800)

    pic = Image.open(pic_upload)
    pic.thumbnail(output_size)
    pic.save(filepath)

    return storage_filename
