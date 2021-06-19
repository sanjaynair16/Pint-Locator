#%%
from bokeh.models.markers import X
from pydeck.data_utils.viewport_helpers import compute_view

import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import numpy as np
import pandas as pd
import tb_func
from tb_func import clean_up
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import pydeck as pdk

# This variable is to be toggle by programmer to
# choose between using actual location given by user's device
# or a hard coded location (user_lat, user_lon)
# for testing or debugging purpose
use_true_loc = False

# Greeting the user on streamlit
st.header("Fancy a drink?")
st.write("Get recommendations close to your location")

# # Codes for the button to get user location
# loc_button = Button(label="By your location")
# loc_button.js_on_event(
#     "button_click",
#     CustomJS(
#         code="""
#     navigator.geolocation.getCurrentPosition(
#         (loc) => {
#             document.dispatchEvent(new CustomEvent("GET_LOCATION", {detail: {lat: loc.coords.latitude, lon: loc.coords.longitude}}))
#         }
#     )
#     """
#     ),
# )
# result = streamlit_bokeh_events(
#     loc_button,
#     events="GET_LOCATION",
#     key="get_location",
#     refresh_on_update=False,
#     override_height=75,
#     debounce_time=0,
# )


# # # Code for extraction the user's location, either from
# # # user's actual device location, or a hard coded location
# # # depending on the value of the variable use_true_loc
# if result:
#     if "GET_LOCATION" in result:
#         location_dict = result.get("GET_LOCATION")
#         # just printing the location on the screen
#         st.write((result.get("GET_LOCATION")))
#         # logic for using real or a hard coded location

# Following will not be run until we have managed to get actual user location
if use_true_loc:

    user_lat = location_dict["lat"]
    user_lon = location_dict["lon"]
# The following else clause will be used to simulate the user location
else:
    st.header("Please Choose Location:")
    loc_dict = {
        "London Bridge": (51.507944497988106, -0.08773837772117324),
        "London Borough Market": (51.50561624055301, -0.09063333428683126),
        "Big Ben": (51.50144104325109, -0.12433133560265978),
        "The Shard": (51.50464687935303, -0.08647853557758274),
        "Trafalgar Square": (51.508120086680684, -0.12778605673404655),
        "London Eye": (51.503399, -0.119519),
        "Camden Town": (51.539, -0.1426),
        "Greenwich Market": (51.4816, -0.0090),
        "Natural History Museum": (51.49957137895956, -0.1679937932383761),
        "Shoreditch": (51.52319050104872, -0.07767945403694568),
    }
    user_loc = st.selectbox("Where are you?", list(loc_dict.keys()))
    user_lat = loc_dict[user_loc][0]
    user_lon = loc_dict[user_loc][1]

######## debugging codes
# st.write(f"user_lat is {user_lat}, of type {type(user_lat)}")
# st.write(f"user_lon is {user_lon}, of type {type(user_lon)}")
########

# creating the vector of user location for distance calculation
user_lat_lon_vector = np.array([user_lat, user_lon])

######## debugging codes
# st.write(f"user lat lon vector is : {user_lat_lon_vector}")
########


########################################################
# Reading the Pubs in London dataframe
@st.cache(suppress_st_warning=True)
def read_london_data():
    df_greater_london = pd.read_csv("greater_london_pub.csv")
    return df_greater_london


df_greater_london = read_london_data()
########################################################


####### DESCRIPTION OF GENERAL WORK FLOW ######
# STEP 1: df_greater_london        ---extraction--->
# STEP 2:   df_for_calculation     ---scaling--->
# STEP 3:       df_scaled          ---Kmean predict--->
# STEP 4:           df_scaled(add cluster column)     ---func retrieve_releveant_cluster()--->
# STEP 5:             pub_clusters                   ---pub_clusters.merge(df_greater_london)--->
# STEP 6:                  pub_names
# STEP 7:                       Plotting on map (duplicate locations but different pub is possible)
# STEP 8:                           Provide google map links to user selected pub


@st.cache(suppress_st_warning=True)
def scale_predict_find_clusters(df_greater_london):
    ############### STEP 1 ###############
    #  Here we extract only the name, fas_id, latitude and longitude from the
    #  main dataframe for calculation
    df_for_calculation = df_greater_london[["name", "fas_id", "latitude", "longitude"]]
    ############### END STEP 1 ###########

    # A copy of the df_for_calculation is made for calcalulation?
    data_frame = df_for_calculation.copy()

    ############### STEP 2 ###############
    # Scaling Dataframe, then call it df_scaled, it will only contain the latitude and longitude column
    sds = StandardScaler()
    df_scaled = pd.DataFrame(sds.fit_transform(data_frame[["latitude", "longitude"]]))
    df_scaled.columns = ["latitude", "longitude"]

    # Add a fas_id column to the df_scaled dataframe
    df_scaled["fas_id"] = data_frame["fas_id"]
    ############### END STEP 2 ###############

    ######## debugging codes
    # st.write("The scaled Dataframe is: ")
    # st.write(df_scaled)
    ########

    ############### STEP 3 ###############
    # Creating kmeans model, random_state is set to 42 for reproducible result for debugging
    km = KMeans(n_clusters=240, init="k-means++", random_state=42)

    # Compute the clusters based on longitude and latitude features
    X_sample = df_scaled[["latitude", "longitude"]].sample(frac=1)
    km.fit(X_sample)
    # st.write("done kmeans")

    # Creating column with different clusters within dataset
    df_scaled["cluster"] = km.predict(df_scaled[["latitude", "longitude"]])
    ############### END STEP 3 ###############
    return sds, km, df_scaled


sds, km, df_scaled = scale_predict_find_clusters(df_greater_london)


# @st.cache(suppress_st_warning=True)
# def find_user_cluster(sds, km, df_scaled, user_lat, user_lon, df_greater_london):
############### STEP 4 ###############
pub_clusters = tb_func.retrieve_relevant_cluster(sds, km, df_scaled, user_lat, user_lon)
# st.write("User belong to the following cluster: ")
# st.dataframe(pub_clusters)
############### END STEP 4 ###############

############### STEP 5 ###############
pub_names = pub_clusters.merge(df_greater_london, on=["fas_id"], how="left")

pub_names = pub_names[
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

# We create a fas_id_name column of type(str) in order to allow selection by user
# and reverse look up for pub info
pub_names["fas_id_s"] = pub_names["fas_id"].astype(str)
pub_names["fas_id_name"] = pub_names[["fas_id_s", "name"]].agg(" ".join, axis=1)

#     return pub_names


# pub_names = find_user_cluster(sds, km, df_scaled, user_lat, user_lon, df_greater_london)


######## debugging codes
# st.write("The follow dataframe is the info of the pubs the user belong to")
# st.dataframe(pub_names)
######## end of debugging codes

############### END STEP 5 ###############

max_display = min(10, len(pub_names))


############### STEP 6 ###############
# If user belongs to a cluster more than 10 pub, display max 10 pub; otherwise display all pub (would be <= 10)

# Create a new DataFrame call df from slicing the pub_names DataFrame row-wise to a total of max_display number of row
df = pub_names[["latitude_y", "longitude_y", "name"]].loc[0:max_display, :]
# Naming the columns
df.columns = ["lat", "lon", "name"]
# st.dataframe(df)

######## debugging codes
# st.write("df is ")
# st.dataframe(df)
######## end of debugging codes
ICON_URL_location = (
    # "https://upload.wikimedia.org/wikipedia/commons/c/c4/Projet_bi%C3%A8re_logo_v2.png"
    "https://upload.wikimedia.org/wikipedia/commons/e/e7/2017-fr.wp-green-pin.svg"
)
ICON_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/c/c4/Projet_bi%C3%A8re_logo_v2.png"
)

icon_data = {
    # Icon from Wikimedia, used the Creative Commons Attribution-Share Alike 3.0
    # Unported, 2.5 Generic, 2.0 Generic and 1.0 Generic licenses
    "url": ICON_URL,
    "width": 242,
    "height": 242,
    "anchorY": 242,
}
present_loc_icon_data = {
    "url": ICON_URL_location,
    "width": 242,
    "height": 242,
    "anchorY": 242,
}


df_present_loc = pd.DataFrame(
    [[user_lat, user_lon, "You're here"]], columns=["lat", "lon", "name"],
)
df_present_loc["icon_data"] = None
for i in df_present_loc.index:
    df_present_loc["icon_data"][i] = present_loc_icon_data
# st.dataframe(df_present_loc)

df["icon_data"] = None
for i in df.index:
    df["icon_data"][i] = icon_data

# st.dataframe(df)

# Plotting max_display number of pubs on a map
API_KEY = "pk.eyJ1IjoiY2xpZmYwMDEiLCJhIjoiY2twZ2hmbHJvMDUyYTJ1cXo0Zm9keWYzYiJ9.JUVgeGVqkgnXC8JFuLAWHg"
st.pydeck_chart(
    pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=compute_view(df[["lon", "lat"]]),
        layers=[
            # pdk.Layer(
            #     "HexagonLayer",
            #     data=df,
            #     get_position="[lon, lat]",
            #     radius=200,
            #     pickable=True,
            #     extruded=True,
            # ),
            # pdk.Layer(
            #     "ScatterplotLayer",
            #     data=df,
            #     get_position="[lon, lat]",
            #     get_color="[200, 30, 0, 160]",
            #     get_radius=1000,
            #     radius_max_pixels=10,
            # ),
            pdk.Layer(
                type="IconLayer",
                data=df,
                get_icon="icon_data",
                get_size=4,
                size_scale=15,
                get_position=["lon", "lat"],
                pickable=True,
            ),
            pdk.Layer(
                type="IconLayer",
                data=df_present_loc,
                get_icon="icon_data",
                # icon_atlas="location.png",
                get_size=4,
                size_scale=15,
                get_position=["lon", "lat"],
                pickable=True,
            ),
        ],
        tooltip={"text": "{name}"},
    )
)


############### END OF STEP 6 ###############

#####################################################
# User selects bar they want to visit by (fas_id and name)
# Collect the lat and lon of the pub
# Return a link filled with lat and lon of the pub

st.subheader("Select a pub and we'll send you the directions!")
# The following line allow user to choose from a list of "fas_id_name"
bar_id_name = st.selectbox(
    "Choose your bar: ", pub_names["fas_id_name"].iloc[:max_display]
)


######## debugging codes
# st.write("bar_id_name is:", bar_id_name)
######## end of debugging codes

# Filter out the single pub that the use has selected, from the pub_names dataframe
selected_bar = pub_names[pub_names["fas_id_name"] == bar_id_name]
selected_bar.reset_index(inplace=True)

######## debugging codes
# st.write(selected_bar)
######## end of debugging codes

# Printing the Pub Details for the user
st.subheader("Pub details")
st.write(f"Name: {selected_bar['name'].get(0)}")
st.write(f"Address: {selected_bar['address'].get(0)}")

# Extract the lat and long of that pub in order to construct a Google map link
latitude = selected_bar.iloc[0, 6]
longitude = selected_bar.iloc[0, 7]

URL = "https://maps.google.com/?q=" + str(latitude) + "," + str(longitude)

st.write(f"Navigation: {URL}")
st.write(f"Have fun and drink responsibly ;)")
#####################################################
