#%%
from scipy.spatial.distance import euclidean
from scipy.spatial.distance import cityblock
from keras.preprocessing import image
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn import metrics
from sklearn.metrics import pairwise_distances
from sklearn.metrics import silhouette_score
import re
import pandas as pd
import numpy as np
import streamlit as st

#%%
# Since some of the data in the latitude and longitude column is corrupted (e.g. showing '\\N' instead of a string in the form of a latitude)
# This function is created to be applied to each indivdual cells in the latitude and longitude column to clean up.
# It's aim is to convert the latitude / longitude in string format into float format by type casting, thereby facilitating the scaler that will be applied
# later on.  If the cell is corrupted, it will return np.nan so that the dropna() method can be applied to remove those rows later on.


def clean_up(s):
    # take a string s, if the form of the string is in %d\.%d (that is, for example, "51.97039", return float(s), otherwise return np.nan
    """Description of clean_up function

    Since some of the data in the latitude and longitude column is corrupted
    (e.g. showing '\\N' instead of a string in the cell of a latitude)

    This function is created to be applied to each indivdual cells in the 
    latitude and longitude column to clean up.

    It aims to convert the latitude / longitude in string format into float format 
    by type casting, thereby facilitating the scaling that will be applied
    later on.  If the cell is corrupted, it will return np.nan so that the dropna() 
    method can be applied to remove those rows later on.

    Parameters:
    s (string) : this is intended to be the string contained in the cell of the
                 dataframe's latitude / longitude column. e.g. "51.507728802993"

    Returns:
    float(l) if s is in the intended format, i.e. "\d+.\d+"
    np.nan if s is in any other format
    """
    if re.search(r"\d+.\d+", s) != None:
        return float(s)
    else:
        return np.nan


# We only want to look at the londen area, so we will extract only those row with
# "local_authority" of the following list obtained from wikipedia

greater_london_borough = [
    "City of London",
    "City of Westminster",
    "Kensington and Chelsea",
    "Hammersmith and Fulham",
    "Wandsworth",
    "Lambeth",
    "Southwark",
    "Tower Hamlets",
    "Hackney",
    "Islington",
    "Camden",
    "Brent",
    "Ealing",
    "Hounslow",
    "Richmond upon Thames",
    "Kingston upon Thames",
    "Merton",
    "Sutton",
    "Croydon",
    "Bromley",
    "Lewisham",
    "Greenwich",
    "Bexley",
    "Havering",
    "Barking and Dagenham",
    "Redbridge",
    "Newham",
    "Waltham Forest",
    "Haringey",
    "Enfield",
    "Barnet",
    "Harrow",
    "Hillingdon",
]
#%%
def load_pub_data(path):
    """Function for loading the csv into a dataframe

    1. Create the DataFrame with the read_csv function
    2. The csv file is passed via the path argument
    3. Clean the dataframe

    Parameters:
    path   : absolute/relative path to the csv file


    Returns:
    df_greater_london : dataframe containing only the pubs in the greater london area

    """
    df_uk = pd.read_csv(path)

    return df_uk


load_pub_data("greater_london_pub.csv")
#%%
def retrieve_relevant_cluster(sds, km, data_frame, latitude, longitude):

    """This function takes in a dataframe with columns["name", "fas_id", "latitude", "longitude"]
    1. Scales the data
    2. Creates KMean model
    3. Fit model
    4. Use prediction to create a new column called "cluster"

    Parameters:

    sds            : StandardScaler object trained already with a dataframe containing the lats and longs of all the pubs.
    km             : trained KMean model 
    data_frame     : Pandas Dataframe with pub information ["name", "fas_id", "latitude", "longitude"]
    latitude       : float, user input or location, latitude of the user
    longitude      : float, user input or location, longitude of the user

    Returns:

    closest_cluster : Pandas DataFrame with a new column of the respective clustor of the pub in each row
                        ["fas_id", "latitude", "longitude", "cluster"]

    """
    # initializing the vector for the user's location
    v = np.array([[latitude, longitude]])

    # scale the vector for the user's location
    v_transform = sds.transform(v)

    # Using clusters to predict where coordinates best fit in
    predicted_clusters = km.predict(v_transform)

    # create another dataframe where the "cluster" is closest to the user location
    closest_cluster = data_frame[data_frame["cluster"] == predicted_clusters[0]]
    return closest_cluster


def return_pub_name(pub_clusters, df_greater_london):
    """This function take in the DataFrame relevant to the predicted cluster calculated from the user's input
    returns the name and address of the pubs in the cluster in the form a of a DataFrame

    Parameter:
    pub_clusters   :  Pandas DataFrame containing ["fas_id", "latitude", "longitude", "cluster"] 

    Returns:
    returned_names :  Single Row dataframe containing a pub name

    """
    # converting ID from float to int
    st.write("1")
    print("1")
    st.write(pub_clusters.info())
    pub_clusters.loc[:, "fas_id"] = pub_clusters["fas_id"].astype(int)
    print("/1")
    st.write("/1")

    # Merge to original dataframe based on ID
    st.write("2")
    print("2")
    pub_names = pub_clusters.merge(df_greater_london, on=["fas_id"], how="left")
    st.write("/2")
    print("/2")

    st.write("3")
    returned_names = pub_names[
        [
            "fas_id",
            "name",
            "address",
            "postcode",
            "local_authority",
            "latitude_y",
            "longitude_y",
        ]
    ]
    st.write("/3")
    return returned_names
