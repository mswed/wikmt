/*
 ****************************************************************************************************************************
 * WWTP OPERATIONS
 * **************************************************************************************************************************
 */

/* Search WWTP by date only
 * @param {string} startDate - sampling start date
 * @param {string} endDate - sampling end date
 * @returns {object} - state boundires and risk factors
 * */
async function searchWWTPByDates(startDate = '2024-12-01', endDate = '2024-12-30') {
  try {
    res = await axios.post('/search/dates', {
      start_date: startDate,
      end_date: endDate,
    });
  } catch (error) {
    if (error.status === 404) {
      showToast(`No records found for ${formatDate(startDate)}-${formatDate(endDate)}`, 'Error', 'danger');
    }
  }

  return res.data;
}

/* Search WWTP by date and location
 * @param {string} address - address to search for
 * @param {string} startDate - sampling start date
 * @param {string} endDate - sampling end date
 * @returns {object} - county boundires and risk factors
 * */
async function searchWWTPByLocationAndDates(address, startDate = '2024-12-01', endDate = '2024-12-30') {
  // Run a search on the api. This calls the flask server.
  try {
    const res = await axios.post('/search/location-dates', {
      start_date: startDate,
      end_date: endDate,
      address: address,
    });
    return res.data;
  } catch (error) {
    if (error.status === 404) {
      showToast(`No records found for ${formatDate(startDate)}-${formatDate(endDate)}`, 'Error', 'danger');
    }
  }
}

/*
 ****************************************************************************************************************************
 * MAP SEARCH OPERATIONS
 * **************************************************************************************************************************
 */

/*
 * Execute a search and update the map based either on an address or its mapboxId
 * @param {string} address - search address
 * @param {string} mapboxId - the addresses mapboxId
 * @param {string} start_date - first date of sampling
 * @param {string} end_date - last date of sampling
 * @retuns {Array} [wwtpStats, county] - wwtp statistics for the county or null if a US wide search, and a county name
 * */
async function performSearch(address = null, mapboxId = null, startDate, endDate) {
  let wwtpStats = null;
  let jurisdiction, county;

  if (address && address.length > 0 && mapboxId && mapboxId.length > 0) {
    // Find and zoom on the address
    [jurisdiction, county] = await searchAddress(mapboxId);

    // Convert the state to its fips
    const state_fips = await axios.get('/fips', {
      params: { state: jurisdiction },
    });

    // Search the API for counties borders and statistical data
    wwtpStats = await searchWWTPByLocationAndDates(jurisdiction, startDate, endDate);
    await updateCountiesMap(wwtpStats);
    // Search for county statistics in that state
  } else {
    // We are looking at a map of states
    const data = await searchWWTPByDates(startDate, endDate);
    await updatStatesMap(data);
    await hideCounties();
    map.flyTo({
      center: [-98.5795, 39.8283],
      zoom: 3,
      duration: 6000,
      essential: true,
    });
  }

  return [wwtpStats, county];
}

/*
 * Parse records to get county data so it can be displayed
 * @param {string} records - geojson records of county data
 * @param {string} county_name - county name from mapbox.
 * @ returns { risk, facility_count, monitored_population, risk_category, risk_trend } - county data
 * */
async function getCountyData(records, county_name) {
  // Since we don't get a fips we need to search by name. The name might have some
  // text in it that we do not need so we clean it up
  let short_county = county_name;
  let region_type = null;
  console.log('Got county name', county_name);

  // const short_county = county_name.replace('County', '').trim();
  if (county_name.includes('Parish') || county_name.includes('County')) {
    const name_split = county_name.split(' ');
    if (name_split.length > 2) {
      // We a "complex" name
      short_county = name_split.slice(0, -1).join(' ');
    } else {
      short_county = name_split[0];
    }
    region_type = name_split.pop();
  }
  console.log('final name is', short_county);
  for (rec of records) {
    if (region_type) {
      if (rec.properties.NAME === short_county && rec.properties.LSAD === region_type) {
        return rec.properties;
      }
    } else {
      if (rec.properties.NAME === short_county) {
        return rec.properties;
      }
    }
  }
}

/*
 * Search the Mapbox API based on a mapboxId and zoom on it
 * @param {string} mapboxId - location id from the API
 * @ returns [state, county] - state and county names
 * */
async function searchAddress(mapboxId = null) {
  let res;
  res = await axios.post('/search/find_address_by_id', { mapboxId });

  if (res.data.success) {
    // Get the search coordinates and state
    let county;
    const features = res.data.data.features;
    const firstResult = features[0];

    const state = firstResult.properties.context.region.name;

    // Get county info
    if (firstResult.properties.context.district) {
      county = firstResult.properties.context.district.name;
    } else if (firstResult.properties.context.region) {
      county = firstResult.properties.context.region.name;
    } else {
      county = null;
    }

    const coordinates = firstResult.geometry.coordinates;

    // Combine this into find address
    const fips_info = await axios.get('/fips', { params: { state } });
    // Enable counties
    showCounties(fips_info.data.fips);

    // Look for a bounding box
    const bbox = firstResult.properties.bbox;
    if (bbox) {
      // Fit the map to the bounding box
      map.fitBounds([bbox[0], bbox[1], bbox[2], bbox[3]], { padding: 50 });
    } else {
      // We did not find a bounding box
      const placeType = firstResult.feature_type;
      let zoom = 18;

      switch (placeType) {
        case 'country':
          zoom = 3; // Country level
          break;
        case 'region': // State level
          zoom = 5;
          break;
        case 'district': // County level
          zoom = 8;
          break;
        case 'place': // City level
          zoom = 11;
          break;
        case 'neighborhood': // neighborhood level
          zoom = 14;
          break;
        case 'street': // Street level
          zoom = 16;
          break;
        case 'address': // House level
          zoom = 18;
          break;
      }
      map.flyTo({
        center: coordinates,
        zoom: zoom,
        duration: 6000,
        essential: true,
      });
    }
    return [state, county];
  }
}

// Get counties json data from Flask server and draw their boundires on the map
async function showCounties(fips) {
  res = await axios.get('/counties', { params: { fips } });

  const counties = map.getSource('counties');
  if (!counties) {
    // Add the counties source
    map.addSource('counties', {
      type: 'geojson',
      data: res.data,
    });
  } else {
    counties.setData(res.data);
  }

  const countiesFillLayer = map.getLayer('county-fills');
  if (!countiesFillLayer) {
    // Add county fill layer
    map.addLayer({
      id: 'county-fills',
      type: 'fill',
      source: 'counties',
      paint: {
        'fill-color': 'white',
        'fill-opacity': 0.1,
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

async function hideCounties() {
  // Get counties json data from Flask server and draw their boundires on the map
  const countiesFillLayer = map.getLayer('county-fills');
  if (countiesFillLayer) {
    // Remove county fill layer
    map.removeLayer('county-fills');
  }
  const countiesSolidLayer = map.getLayer('counties_solid');
  if (countiesFillLayer) {
    // Remove county fill layer
    map.removeLayer('counties_solid');
  }
  const countiesBoundryLines = map.getLayer('county-borders');
  if (countiesBoundryLines) {
    // Add county boundary lines
    map.removeLayer('county-borders');
  }
}
