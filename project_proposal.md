# Project Proposal

## Will It Kill Me, Though?
Will it kill me, though? is a website for medical statistics. As a first step it will focus on Covid 19 statistics in the US. The site will allow users to view a map of current spread information. Users will also be able to save searches for specific regions, with specific considerations , for example age group, pre-existing conditions and so on. 

### Tech Stack
The site will use Flask, PostgreSQL, SQLAlchemy for its back-end and JavaScript, HTML, etc for its front-end. 

### Users
The site, at first, will be geared toward US users who are interested in the current Covid statistic in their area, or in areas they'd like to travel to. 

### Data
The site will use the CDC API to access Covid 19 statistic in the US. The map will be driven by Google Maps API. 


## Project Breakdown 
This is a very preliminary breakdown, most of the items will change as the project progresses. 

### Database Schema
#### Users
user_id - primary key
user_name
email
age
location
#### searches
search_id
user_id - foreign key to users table
address
age
illness - needs a better name. This will be the top level search Covid, Flu, Car Accidents, etc
existing conditions? Need to check what is supported by the API

### Data Sources
#### CDC Covid Database
https://dev.socrata.com/foundry/data.cdc.gov/vbim-akqf

#### Google Maps
https://developers.google.com/maps

### Setting up the backend and database
TBD

### Setting up the frontend
TBD

### Functionality
  - User login and sign up
  - Uploading a user profile picture
  - Searching a specific area for covid cases
  - Ability to save the searches
  - A map showing color base status of covid in different regions, depending on what is available in the API. At the very minimum state level map. 
  - Graphs showing covid statistic in selected area (number of cases, deaths, etc )

### Stretch Goals
- Add different conditions, Flu, Car accidents, Whatever the CDC tracks
- Add Covid info for other countries 
