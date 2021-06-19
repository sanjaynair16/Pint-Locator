# Pint-Locator

# Description:

A pub recommendation system used to help users find pubs near them based on their location.

# Table of Contents:
- Business Objective
- Data Collection 
- Pre-Processing
- Exploratory Data Analysis
- Model Development & Predictions
- Model Deployment (Streamlit)
- Challenges & Next Steps

# Business Objective: 

With people across the UK itching to get out from lockdown as a result of Covid-19 and understanding that pubs plays a significant role in English culture, this streamlit app is designed to recommend and help you find bars near you. By doing so, we hope to achieve the following:
  - Help customers find new pubs
  - Help local pubs find new potential customers
  - Assist tourist that might be unfamiliar with the area looking to visit a pub

<img src="image/intro" width="600"> 

# Data Collection

The data was collected using the open-source platform Kaggle on every pub within the UK

Link: https://www.kaggle.com/rtatman/every-pub-in-england

Overview: This dataset includes information on 51,566 pubs in the UK

Data Upload Year: 2017 (outdated but used for learning purpose)

Contents:
- fsa_id (int): Food Standard Agency's ID for this pub.
- name (string)L Name of the pub
- address (string): Address fields separated by commas.
- postcode (string): Postcode of the pub.
- easting (int)
- northing (int)
- latitude (decimal)
- longitude (decimal)
- local_authority (string): Local authority this pub falls under.

![data_collection](https://user-images.githubusercontent.com/70877020/122177946-adcb0580-ceb8-11eb-8ca1-485b8c5f2b4a.png)

# Pre-Processing

The following screenshots explain the pre-processing done before further analysis was conducted on the data. For the purpose of this project, we focused on extracting data just from London.


![preprocess-1](https://user-images.githubusercontent.com/70877020/122177922-a73c8e00-ceb8-11eb-80c2-a0c687cbcc13.png)


![preprocess-2](https://user-images.githubusercontent.com/70877020/122177908-a3107080-ceb8-11eb-945c-0e185107c877.png)


# Exploratory Data Analysis

A short EDA was conducted on the data to better understand the data-set.

![eda-1](https://user-images.githubusercontent.com/70877020/122177883-9be96280-ceb8-11eb-8171-34b2ebc8c542.png)


![eda-2](https://user-images.githubusercontent.com/70877020/122177840-90963700-ceb8-11eb-8fae-e1fc5219de9f.png)


# Model Development & Predictions

A K-means model was used to cluster the bars together based on their latitude and longitiude. The following steps were taken to build the model:

## Step 1) Selecting the relevant columns needed for the model:

- name: for teams personal reference
- fas_id: pub ID number
- latitude: latitude of each pub
- longitude: longitude of each pub

![selected_columns](https://user-images.githubusercontent.com/70877020/122177792-870ccf00-ceb8-11eb-9dac-7f1ff4f87b2a.png)

## Step 2) Applying Standard Scaler to the longitude and latitiude columne to prevent the model from overweighting particular features due to drastic differneces between the long and lat figures.

![latlong](https://user-images.githubusercontent.com/70877020/122177742-7c523a00-ceb8-11eb-8a11-b9423d307c02.png)

![scaler](https://user-images.githubusercontent.com/70877020/122177712-74929580-ceb8-11eb-801f-d8c9416be8f5.png)

## Step 3) Applying K-means clusters to group pubs together based on distnace between longitiude and latitude between each pub within the data-set.

The following code used K-means clustering to create a column "cluster" within the dataframe, which assigned each pub to 1 of 200 clusters.

![Screenshot 2021-06-16 at 15 41 49](https://user-images.githubusercontent.com/70877020/122178708-68f39e80-ceb9-11eb-98e4-b59ca54eb8f3.png)

## Step 4) Used silhouette_score to measure how similar a pub is to its own cluster, which can be used to optimise the number of clusters generated.

After applying the silhoette score method to optimise the models, we can see that an optimal number of clusters is already reached before 50 clusters. This can be seen in the elbow graph below:

![elbow](https://user-images.githubusercontent.com/70877020/122177670-6b092d80-ceb8-11eb-9682-bd972ff81deb.png)

However, when selecting the number of clusters to use we had to be mindful that we needed a large number of clusters to split the pubs into smaller groups so that the pubs recommended to the user would be more specific to the location. Therefore, 248 clusters was used which gave us a silhouette score of 0.43.

## Step 5) Using the clusters to make predictions based on the users input location, returning the pubs that are closet to the user.

The following function can be broken down into the following:

1) Initialising the vector based on the users' input location
2) Scale the vector for the user's location
3) Use clusters to predict where coordinates best fit in
4) Create another dataframe with the "cluster" that is closest to the users' location

![Screenshot 2021-06-16 at 15 43 49](https://user-images.githubusercontent.com/70877020/122179007-b243ee00-ceb9-11eb-99ec-5d1d1072749c.png)

## Step 6) Returning the Name, Address, Postcode, Local_Authority (Borough), Unscaled Latitiude and Unscaled Longitude 

The following function can be broken down into the following:
1) Converting the pub ID from float to integer to match the original dataframe ID data type
2) Take ID from the list of pubs selected that are closest to the users' input location based on cluster
3) Return original dataframe with pub names, addresses, postcodes, local authorities, unscaled latitude's and unscaled longitude's

![Screenshot 2021-06-16 at 15 48 57](https://user-images.githubusercontent.com/70877020/122179863-79584900-ceba-11eb-8278-1ad1f2c8b263.png)


# Model Deployment

Below features a demonstration of the deployed model using Streamlit. 

## Finding Pubs

For the purpose of this demonstration, the selected locations were pre-set to popular spots accross london. The user would select a location and it would return a map with the pubs that are currently surrounding him/her.

![ezgif com-gif-maker](https://user-images.githubusercontent.com/70877020/122635299-99377900-d115-11eb-8ac3-cd2648090c09.gif)

## Selecting Location

The user would then select a pub they would like to visit. Once they have choosen, the will recieve the address and google maps link to direct them.

![ezgif com-gif-maker (1)](https://user-images.githubusercontent.com/70877020/122635531-10214180-d117-11eb-93e7-aed106b5ab0f.gif)

![ezgif com-gif-maker (2)](https://user-images.githubusercontent.com/70877020/122635534-144d5f00-d117-11eb-9d0c-f7e25b68c5e7.gif)


# Challenges & Next Steps

Challenges:

1) The data set is 4 years old and isn't updated in real-time, and therefore some of the suggested pubs could have moved or no longer exist
Solution: Potentially using API instead (Google Maps Paid API service)

2) Limitation of the model is the cluster sizes are different, with some clusters being significantly larger than others as some pubs were located in highly saturated areas.

Next Steps:

1) Integrate Google Maps API to provide real-time information on pubs surrounding the user. 

2) Deploy model as a Mobile APP with additional features
    - Features could include booking service, additional information on pub (price-range, ratings, events), call ride home service (Uber/Taxi).
    - Other future features could include pub-crawl game, ticking feature to show pubs previously visited.
