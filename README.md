# About Will It Kill Me Though

Will It Kill Me Though is a small site with big dreams. At the moment it offers some statistics on the spread of COVID in the US. It takes data from the CDC waste water treatment plants that sample the existence of COVID in the sewers and displays it on a map. The spread is measured in five categories:

- Very Low
- Low
- Medium
- High
- Very High

Searching for a specific address will also show county-level data which includes the number of treatment plants in the county, the population these facilities serve, and whether or not the spread is getting worse, better, or is static. The last statistic is simply a comparison between the latest sample and the one before it.

To make depressing statistics more entertaining, if you provide the site with your demographic details (year of birth, sex, etc.), it will use historic mortality data from the CDC to give an opinion on whether the found spread of COVID will kill you.

Once again there are 5 categories:

- I don't think so
- Probably not
- Maybe?
- Probably
- Absolutely it will

In the rare case that no spread data is provided (like the ENTIRE state of
North Dakota?!), you will get a 6th category: "I'm surprised you sure you're still
alive"

As these categories suggest, the results should not be taken too seriously. While the spread of COVID data is (or at least should be) reliable, as should the historical mortality rates, the risk of death calculation is just a bunch of extrapolated multipliers used to give a rough, and hopefully funny, estimate.

In the future, I hope the site will include more things that might kill you, such as bird flu, car accidents, falling off ladders, and all the other insane statistics provided by the CDC.

---

_Disclaimer: This website is for entertainment purposes only and should not be used as a substitute for professional medical advice. Always consult qualified healthcare providers about your specific health circumstances._

# Live Demo

https://witmt.onrender.com

# API Info

The website uses two APIs.

## Covid Waste Water Data from the CDC

- https://data.cdc.gov/resource/2ew6-ywp6.json
- Used to get the spread of Covid in the US, on a state and county level
- Recently the CDC API system was taken down, so there is a basic (and not tested) system in place to fallback to historic data saved on a local database.

## Mapbox

- "https://api.mapbox.com/
- Used to search and display the map

# Features

The site allows the user to:

- Search US states and show Covid spread level
- Search for a specific address in the US, showing County level
- Save the user demographic data, which allows for a death risk calculation based on the demographics and the found county's covid spread info.
- Save user addresses
- Save user searches
- If not logged in: view saved searches by other users

# Walkthrough

When first loading the site a map of the US is displayed with a Covid spread results for the last month. There should also be a ' Latest Saved Searches' section which shows a list of recent saved searches on the site. Clicking on a saved search will focus the map on the search area and show the results on the right side of the site.

The user can register for an account, with optional demographic information. Doing so, and logging in, enables the user to run searches, save addresses and searches.

To view the results of a search, the user can start a search by editing the start and end dates and hitting the 'Search!' button. These searches will show the map of the US with colored statistics on the spread of Covid. The user can also either enter a new address and use it to create a more specific search. Or select an address from their saved addresses list. Once a search is complete, the map will zoom on the searched region, and some results will be displayed on the right side of the screen:

- The user searched only for dates - Date rage will be displayed
- The user searched for a state - Date range will be displayed and the map will zoom on the entire state, showing its counties
- The user searched for an address = The map will zoom on the address. The right side will display, date range, address, county information, including name, number of Waste Water Facilities, the spread of Covid, the risk trend and a "Risk of death" information under a card called: Will it kill me, though?

The results panel also includes buttons for saving the address or the entire search (in which case unregistered users will be able to use it to see the results).

The saved searches panel works a lot like the saved searches displayed for unregistered users but also allows the user to delete the search.

# Stack

## Backend

- Flask
- PostgreSQL for data persistence
- Flask-WTF for form handling and validation

## Frontend:

- Bootstrap for responsive UI components and styling
- JavaScript for client-side interactivity

## Integration:

- Two external APIs

# Setup Instructions

## Initial Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows
```

## Install requirements:

```bash
pip install -r requirements.txt
```

## Database Setup

Create PostgreSQL databases:

```bash
createdb wikmt_db
createdb wikmt_test_db
```

## Data Setup

Run the seed file to create tables and initial data:

```bash
python seed.py
```

Note: If you have the CDC wastewater data file at ./static/data/NWSS_Public_SARS-CoV-2_Wastewater_Metric_Data.csv, the historic data table will also be populated. This allows the application to function without direct access to the CDC API.

## Running the Application

Start the application in debug mode:

```bash
flask run --debug
```

The application will be available at http://localhost:5000 Database integration through PostgreSQL and SQLAlchemy

## Running tests

In the app folder run

```bash
pytest
```

At the moment only the SQLAlchemy models and Flask routes are tested
