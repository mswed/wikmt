const dateRangeCard = document.getElementById('date-range-container');
const dateRange = document.getElementById('date-range');
const foundAddressCard = document.getElementById('found-address-container');
const foundAddress = document.getElementById('found-address');
const foundCountyCard = document.getElementById('found-county-container');
const foundCounty = document.getElementById('found-county');
const deathRiskCard = document.getElementById('death-risk-container');
const deathRisk = document.getElementById('death-risk');
const saveAddressBtn = document.getElementById('save-address');
const saveSearchBtn = document.getElementById('save-search');

/*
 ****************************************************************************************************************************
 * DISPLAY RESULTS
 * **************************************************************************************************************************
 */

/*
 * Display the results of a search in cards on the right most column of the UI
 * @param {string} start_date - first sampling date
 * @param {string} end_date - last sampling date
 * @param {string} address - searched address
 * @param {string} mapboxId - mapboxId of searched address
 * @param {string} county - searched county (optional)
 * @param {object} wwtpStats - wwtp statistics from the search. We access the features array of the object
 * */
async function displayResults(startDate, endDate, address, mapboxId, county = null, wwtpStats = null) {
  // TODO: This needs to be simplified
  await clearResults();

  // Dates card
  if (startDate && endDate) {
    dateRangeCard.classList.remove('d-none');
  } else {
    dateRangeCard.classList.add('d-none');
  }

  dateRange.innerText = `${formatDate(startDate)} - ${formatDate(endDate)}`;
  dateRange.dataset.startDate = startDate;
  dateRange.dataset.endDate = endDate;

  // Address card
  if (address) {
    foundAddressCard.classList.remove('d-none');
  } else {
    foundAddressCard.classList.add('d-none');
  }
  foundAddress.innerText = `${address}`;
  foundAddress.dataset.mapboxId = mapboxId;

  if (foundAddress.innerText.includes('North Dakota')) {
    // TODO: This is dirty, need a nicer solution
    foundCounty.innerHTML = `The address is in <span class="highlight">${county}</span> which does not seem to be collecting any data! I guess they just don't care if you live or die...`;
    deathRisk.innerHTML = `<span style="color: red">I'm surprised you're still alive!</span>`;
    foundCountyCard.classList.remove('d-none');
    deathRiskCard.classList.remove('d-none');
    return;
  }
  if (county !== null) {
    // We have a county display the card
    foundCountyCard.classList.remove('d-none');

    if (wwtpStats !== null) {
      // We got some statistical data process it
      const { facility_count, monitored_population, risk_category, risk_trend, risk_score } = await getCountyData(wwtpStats.features, county);

      // Check if we got any data other than the name of the county
      if (facility_count) {
        foundCounty.innerHTML = `The address is in <span class="highlight">${county}</span> which has <span class="highlight">${facility_count}</span> Waste Water Treatment Facilities monitoring a 
      total polulation of <span class="highlight">${formatNumber(monitored_population)}</span>. The COVID spread level in this county is: <span style="color: ${setRiskColor(risk_category)}">${risk_category}</span> and the risk is <span style="color: ${setTrendColor(risk_trend)}">${risk_trend}</span>`;

        // Show the death risk calcualtion
        const personalDeathRisk = await axios.get('/death', {
          params: { risk_score },
        });

        if (personalDeathRisk.data.success) {
          deathRisk.innerHTML = `<span style="color: ${setDeathRiskColor(personalDeathRisk.data.msg)}">${personalDeathRisk.data.msg}</span>`;
          deathRiskCard.classList.remove('d-none');
        }
      } else {
        // We did not find any county related data other than its name
        foundCounty.innerHTML = `The address is in <span class="highlight">${county}</span> which does not seem to be collecting any data! I guess they just don't care if you live or die...`;
        deathRisk.innerHTML = `<span style="color: red">I'm surprised you're still alive!</span>`;
        deathRiskCard.classList.remove('d-none');
      }
    } else {
      foundCountyCard.classList.add('d-none');
      deathRiskCard.classList.add('d-none');
    }
  } else {
    foundCountyCard.classList.add('d-none');
    deathRiskCard.classList.add('d-none');
  }

  // Save button
  if ((startDate && endDate) || address || county) {
    saveSearchBtn.classList.remove('d-none');
  } else {
    saveSearchBtn.classList.add('d-none');
  }
}

async function clearResults() {
  dateRangeCard.classList.add('d-none');
  foundAddressCard.classList.add('d-none');
  foundCountyCard.classList.add('d-none');
  deathRiskCard.classList.add('d-none');
}
/*
 ****************************************************************************************************************************
 * BUTTONS
 * **************************************************************************************************************************
 */

if (saveAddressBtn) {
  saveAddressBtn.addEventListener('click', async () => {
    // Save the address in the database
    const res = await axios.post('/save/address', {
      address: foundAddress.innerText.replace('Address: ', ''),
      mapbox_id: foundAddress.dataset.mapboxId,
    });
    if (res.data.success) {
      // If we saved create an element in the UI
      const savedAddressesList = document.getElementById('saved-addresses-list');
      const card = document.createElement('div');
      card.classList.add('card', 'list-group-item');
      card.dataset.mapboxId = foundAddress.dataset.mapboxId;
      card.dataset.addressId = res.data.address_id;
      card.innerHTML = `<p class="card-text"> ${foundAddress.innerText}</p>
                        <div class="d-flex justify-content-end gap-2">
                          <button class="btn btn-sm btn-success saved-address-select">Select</button>
                          <button class="btn btn-sm btn-danger saved-address-delete">
                            <i class="bi bi-trash"></i>
                          </button>`;

      // Add event listeners to the card's buttons
      const selectBtn = card.querySelector('.saved-address-select');
      const deleteBtn = card.querySelector('.saved-address-delete');

      selectBtn.addEventListener('click', (evt) => {
        evt.preventDefault();
        selectAddress(selectBtn);
      });

      deleteBtn.addEventListener('click', (evt) => {
        evt.preventDefault();
        deleteAddress(deleteBtn);
      });

      // Add the card to the list
      savedAddressesList.append(card);
    }
  });
}

if (saveSearchBtn) {
  saveSearchBtn.addEventListener('click', async () => {
    const res = await axios.post('/save/search', {
      start_date: dateRange.dataset.startDate,
      end_date: dateRange.dataset.endDate,
      address: foundAddress.innerText,
      mapbox_id: foundAddress.dataset.mapboxId,
    });

    if (res.data.success) {
      // If we saved create an element in the UI
      const savedSearchesList = document.getElementById('saved-searches-list');
      const card = document.createElement('div');
      card.classList.add('card', 'list-group-item');
      card.dataset.searchId = res.data.search_id;
      const searchAddress = foundAddress.innerText !== 'undefined' ? foundAddress.innerText : '';
      card.innerHTML = `<h5 class="card-title">${dateRange.innerText}</h5>
                <p class="card-text">${searchAddress}</p>
                <div class="d-flex justify-content-end gap-2">
                  <button class="btn btn-sm btn-success saved-search-select">
                    Get Stats
                  </button>
                  <button class="btn btn-sm btn-danger saved-search-delete">
                    <i class="bi bi-trash"></i>
                  </button>
                </div>`;

      // Add event listeners to the card's buttons
      const selectBtn = card.querySelector('.saved-search-select');
      const deleteBtn = card.querySelector('.saved-search-delete');

      selectBtn.addEventListener('click', (evt) => {
        evt.preventDefault();
        selectSearch(selectBtn);
      });

      deleteBtn.addEventListener('click', (evt) => {
        evt.preventDefault();
        deleteSearch(deleteBtn);
      });

      // Add the card to the list
      savedSearchesList.append(card);
    }
  });
}

/*
 * Get a color based on a risk level
 * @param {string} risk - risk level
 * @returns {string} - risk color
 * */
function setDeathRiskColor(risk) {
  switch (risk) {
    case "I don't think so":
      return '#143109';
    case 'Probably not':
      return '#FFF700';
    case 'Maybe?':
      return '#FF6A00';
    case 'Probably':
      return '#FF1C1C';
    case 'Absolutly it will':
      return '#FF0099';
    default:
      return 'black';
  }
}
/*
 * Get a color based on a risk level
 * @param {string} risk - risk level
 * @returns {string} - risk color
 * */
function setRiskColor(risk) {
  switch (risk) {
    case 'Very Low':
      return '#143109';
    case 'Low':
      return '#FFF700';
    case 'Medium':
      return '#FF6A00';
    case 'High':
      return '#FF1C1C';
    case 'Very High':
      return '#FF0099';
    default:
      return 'black';
  }
}
/*
 * Get a color based on a trend direction
 * @param {string} trend - the trend direction
 * @returns {string} - trend color
 * */
function setTrendColor(trend) {
  switch (trend) {
    case 'decreasing':
      return 'green';
    case 'static':
      return '#FF6A00';
    case 'increasing':
      return '#FF0099';
    default:
      return 'black';
  }
}
