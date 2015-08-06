import os
import requests
import sys
import time

def get_file(url, fname, directory=None, headers=None, verify=None):
    print("\nDownloading " + fname + " ...")
    if directory != None:
        if directory != "":
            if directory[-1] == "\\":
                directory = directory[:-1]
        if not os.path.exists(directory):
            os.makedirs(directory)
    else:
        directory = ""
    with open(os.path.join(directory, fname), "wb") as f:
        start = time.clock()
        r = requests.get(url, stream=True, headers=headers, verify=verify)
        total_length = r.headers.get('content-length')
        dl = 0
        if total_length is None:
            f.write(r.content)
            print("\nDownload complete.\n")
        else:
            total_length = int(total_length)
            for chunk in r.iter_content(4096):
                dl += len(chunk)
                f.write(chunk)
                speed = str(round(dl / 1024 / (time.clock() - start), 2))
                time_elapsed = time.clock() - start
                progress = "\tSpeed: " + speed + "KB/s" + "\t" +\
                           "Time Elapsed: {0:.{1}f}s".format(time_elapsed, 2) + "\t" +\
                           "{0:.{2}f}KB/{1:.{2}f}KB".format(dl / 1024, total_length / 1024, 2)
                sys.stdout.write("\r%s" % progress)
                sys.stdout.flush()
            print("\nDownload complete.\n")