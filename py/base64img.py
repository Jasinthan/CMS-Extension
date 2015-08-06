import base64
import random
import re
import os
    
def save_to_file(src, directory=""):
    r = random.Random()
    fname = str(r.uniform(0,1))[2:]
    data = re.search("\,.*$", src).group()[1:]
    
    ext = ".png"    
    
    try:
        mimetype = re.search("^data.*\;", src).group()[5:-1]
    except:
        mimetype = "image/png"
        
    if mimetype == "image/png":
        ext = ".png"
    elif mimetype == "image/jpeg":
        ext = ".jpg"    
    elif mimetype == "image/gif":
        ext = ".gif"
    else:
        pass
    
    fname += ext
    with open(os.path.join(directory, fname), "wb") as f:
        f.write(base64.b64decode(data))
    return fname