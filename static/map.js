const STYLE = 'mapbox://styles/wilsonpuddnhead/cm62ks6fp004w01s61sur5mkz';

// The map object needs the access token to work
mapboxgl.accessToken = 'pk.eyJ1Ijoid2lsc29ucHVkZG5oZWFkIiwiYSI6ImNsd2UwY2Y3ZDA3N2Uyam10dmFtMmZmMTkifQ.dGeq-h9UrNpca716xUCzKA';

/*
 ****************************************************************************************************************************
 * MAP OPERATIONS
 * **************************************************************************************************************************
 */

// Create a map object
const map = new mapboxgl.Map({
  container: 'map',
  style: STYLE,
  center: [-98.5795, 39.8283],
  zoom: 3,
});

// On map load we run a default search
map.on('load', async function () {
  await initialSearch();

  return;
});

/* Run an initial search that is based only on dates and update the map
 * @param {string} startDate - sampling start date
 * @param {string} endDate - sampling end date
 * @returns {object} - state boundires and risk factors
 * */
async function initialSearch(startDate = '2024-11-01', endDate = '2024-11-30') {
  // TODO: This should match the form default settings, but the form is might not yet visible
  try {
    // We are updating the states map
    const data = await searchWWTPByDates(startDate, endDate);
    if ('error' in data) {
      throw Error(data.error);
    }
    await updatStatesMap(data);
    displayResults(startDate, endDate);
  } catch (error) {
    console.error('Failed to update map:', error.response?.data?.error || error.message);
  }
}

/* Update the counties map to include risk colors
 * @param {json object} counties_data - jsongeo data with boundires and risk factors
 * */
async function updateCountiesMap(counties_data) {
  // Set a counties source
  const counties = map.getSource('counties');
  if (!counties) {
    // Add the counties source
    map.addSource('counties', {
      type: 'geojson',
      data: counties_data,
    });
  } else {
    counties.setData(counties_data);
  }

  // Set the counties layer
  const layer = map.getLayer('counties_solid');
  if (!layer) {
    map.addLayer({
      id: 'counties_solid',
      type: 'fill',
      source: 'counties',
      paint: {
        'fill-color': ['match', ['get', 'risk_id'], 0, '#143109', 1, '#FFF700', 2, '#FF6A00', 3, '#FF1C1C', 4, '#FF0099', 'white'],
        'fill-opacity': 0.3,
      },
    });
  }

  const countiesBoundryLines = map.getLayer('county-borders');
  if (!countiesBoundryLines) {
    // Add county boundary lines
    map.addLayer({
      id: 'county-borders',
      type: 'line',
      source: 'counties',
      paint: {
        'line-color': '#627BC1',
        'line-width': 0.5,
      },
    });
  }
}

/* Update the states map to include risk colors
 * @param {json object} states_data - jsongeo data with boundires and risk factors
 * */
async function updatStatesMap(states_data) {
  // Set the source
  const source = map.getSource('regions');
  if (source) {
    source.setData(states_data);
  } else {
    map.addSource('regions', {
      type: 'geojson',
      data: states_data,
    });

    // Set the states layer
    const layer = map.getLayer('regions_solid');
    if (!layer) {
      map.addLayer({
        id: 'regions_solid',
        type: 'fill',
        source: 'regions',
        paint: {
          'fill-color': ['match', ['get', 'risk'], 0, '#143109', 1, '#FFF700', 2, '#FF6A00', 3, '#FF1C1C', 4, '#FF0099', 'white'],
          'fill-opacity': 0.3,
        },
      });
    }
  }
}
