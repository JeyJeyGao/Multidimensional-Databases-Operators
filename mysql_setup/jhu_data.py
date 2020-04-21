import urllib
import zipfile
import shutil
import os

GIT_URL = "https://github.com/CSSEGISandData/COVID-19/archive/master.zip"
ZIP_NAME = os.path.join("mysql_setup", "COVID-19.zip")
TEMP_DIR_NAME = os.path.join("mysql_setup", "COVID-19-master")
DIR_NAME = os.path.join("mysql_setup", "COVID-19")


def fetch_data():
    if os.path.exists(ZIP_NAME):
        os.remove(ZIP_NAME)
    if os.path.exists(DIR_NAME):
        shutil.rmtree(DIR_NAME)
    print("Downloading remote data...")
    urllib.request.urlretrieve(GIT_URL, ZIP_NAME)
    print("Unzipping...")
    with zipfile.ZipFile(ZIP_NAME, 'r') as zip_ref:
        zip_ref.extractall("mysql_setup")
    os.rename(TEMP_DIR_NAME, DIR_NAME)
    print("Done.")
