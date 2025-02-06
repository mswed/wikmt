const searchForm = document.getElementById('search-form');

/*
 ****************************************************************************************************************************
 * SEARCH FORM
 * **************************************************************************************************************************
 */

// When a search form is submitted, we collect the form info and run two
// different searches. The first is the address search which gets us the
// New map position. The second is the api search for the actual statistics.
searchForm.onsubmit = async (e) => {
  e.preventDefault();
  // Set up some variable we need to display to the user at the end of the
  // optration
  let mapboxId;

  // Access the form data
  const formData = new FormData(e.target);

  // Access formData as an object
  const fdo = Object.fromEntries(formData.entries());

  // Check if we have any saved address selected
  let targetAddress;
  const selectedSavedAddress = [...document.querySelectorAll('.list-group-item')].find((item) => item.classList.contains('active'));
  if (selectedSavedAddress) {
    mapboxId = selectedSavedAddress.dataset.mapboxId;
    targetAddress = selectedSavedAddress.children[0].innerText;
  } else {
    mapboxId = addressField.dataset.mapboxId;
    targetAddress = fdo.address;
  }

  // Perform the search
  const [wwtpStats, county] = await performSearch(targetAddress, mapboxId, fdo.start_date, fdo.end_date);
  if (wwtpStats && wwtpStats.error) {
    // TODO: We need to let the user know the search failed
  }

  // Display results on right column
  displayResults(fdo.start_date, fdo.end_date, targetAddress, mapboxId, county, wwtpStats);
};

/*
 ****************************************************************************************************************************
 * SAVED ADDRESSES
 * **************************************************************************************************************************
 */

document.querySelectorAll('.saved-address-select').forEach((button) => {
  button.addEventListener('click', (evt) => {
    evt.preventDefault();
    selectAddress(button);
  });
});

document.querySelectorAll('.saved-address-delete').forEach((button) => {
  button.addEventListener('click', (evt) => {
    evt.preventDefault();
    deleteAddress(button);
  });
});

/* Select an address from the addresses list
 * @param {object} element - the button that was clicked
 * */
function selectAddress(element) {
  const card = element.closest('.card.list-group-item');
  // Backup element original state
  const original_state = [...card.classList];

  // Remove active class from all items
  document.querySelectorAll('.saved-address').forEach((item) => {
    item.children[1].children[0].innerText = 'Select';
    item.classList.remove('active');
  });

  if (!original_state.includes('active')) {
    // The element was not selected before so we can make it active now
    element.closest('.card.list-group-item').classList.add('active');
    element.innerText = 'Deselect';
  } else {
    element.innerText = 'Select';
  }
}

/* Delete an address from the addresses list
 * @param {object} element - the button that was clicked
 * */
async function deleteAddress(element) {
  // Remove active class from all items
  document.querySelectorAll('.list-group-item').forEach((item) => {
    item.classList.remove('active');
  });

  const addressCard = element.parentElement.parentElement;
  const addressId = addressCard.dataset.addressId;
  try {
    const res = await axios.post('/delete/address', {
      addressId,
    });

    if (res.data.success) {
      addressCard.remove();
    }
  } catch (error) {
    if (error.status === 401) {
      showToast(error.response.data.msg, 'Error', 'danger');
    }
    if (error.status === 403) {
      showToast(error.response.data.msg, 'Error', 'danger');
    }
    if (error.status === 404) {
      showToast(error.response.data.msg, 'Error', 'danger');
    }

    if (error.status === 409) {
      showToast(error.response.data.msg, 'Error', 'danger');
    }
    if (error.status === 422) {
      showToast(error.response.data.msg, 'Error', 'danger');
    }
    if (error.status === 500) {
      showToast(`An unexpected error has occured: ${error.response.data.msg}`, 'Error', 'danger');
    }
  }
}

/*
 ****************************************************************************************************************************
 * SAVED SEARCHES
 * **************************************************************************************************************************
 */

document.querySelectorAll('.saved-search-select').forEach((button) => {
  button.addEventListener('click', (evt) => {
    evt.preventDefault();
    selectSearch(button);
  });
});

document.querySelectorAll('.saved-search-delete').forEach((button) => {
  button.addEventListener('click', (evt) => {
    evt.preventDefault();
    deleteSearch(button);
  });
});

/* Select a search from the searches list
 * @param {object} element - the button that was clicked
 * */
async function selectSearch(element) {
  document.querySelectorAll('.card.list-group-item').forEach((item) => {
    item.classList.remove('active');
  });
  element.closest('.card.list-group-item').classList.add('active');
  const searchCard = element.parentElement.parentElement;
  const searchId = searchCard.dataset.searchId;
  const searchData = await axios.post('/load/search', { searchId });
  if (searchData.data.success) {
    const data = searchData.data.search;
    data.mapboxId = data.mapboxId === 'undefined' ? null : data.mapboxId;
    data.address = data.address === 'undefined' ? null : data.address;
    const [wwtpStats, county] = await performSearch(data.address, data.mapboxId, data.startDate, data.endDate);
    displayResults(data.startDate, data.endDate, data.address, data.mapboxId, county, wwtpStats);
  }
}

/* Delete a search from the searches list
 * @param {object} element - the button that was clicked
 * */
async function deleteSearch(element) {
  document.querySelectorAll('.card.list-group-item').forEach((item) => {
    item.classList.remove('active');
  });
  const searchCard = element.parentElement.parentElement;
  const searchId = searchCard.dataset.searchId;

  try {
    const searchData = await axios.post('/delete/search', { searchId });
    if (searchData.data.success) {
      searchCard.remove();
    }
  } catch (error) {
    if (error.status === 401) {
      showToast(error.response.data.msg, 'Error', 'danger');
    }
    if (error.status === 403) {
      showToast(error.response.data.msg, 'Error', 'danger');
    }
    if (error.status === 404) {
      showToast(error.response.data.msg, 'Error', 'danger');
    }

    if (error.status === 422) {
      showToast(error.response.data.msg, 'Error', 'danger');
    }
    if (error.status === 500) {
      showToast(`An unexpected error has occured: ${error.response.data.msg}`, 'Error', 'danger');
    }
  }
}
