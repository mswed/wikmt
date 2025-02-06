const addressField = document.getElementById('address');
const addressDropdown = document.getElementById('address-dropdown');
let searchTimeOut;
let selectedAddressIndex;

/*
 ****************************************************************************************************************************
 * ADDRESS FIELD SEARCH SETUP WITH DROPDOWN
 * **************************************************************************************************************************
 */

addressField.addEventListener('keyup', async (e) => {
  // First some navigation options
  if (['ArrowUp', 'ArrowDown', 'Enter', 'Escape'].includes(e.key)) {
    if (e.key === 'ArrowUp') {
      // Go up in the list
      e.preventDefault();
      selectedAddressIndex = Math.max(selectedAddressIndex - 1, 0);
      updateAddressSelection();
    } else if (e.key === 'ArrowDown') {
      // Go down the list
      e.preventDefault;
      selectedAddressIndex = Math.min(selectedAddressIndex + 1, addressDropdown.children.length - 1);
      updateAddressSelection();
    } else if (e.key === 'Enter') {
      // Select an item in the list
      if (selectedAddressIndex >= 0) {
        // We have an item selected
        const selectedItem = addressDropdown.children[selectedAddressIndex];
        addressField.value = selectedItem.textContent;
        await clearSelectedAddreses();
        hideDropdown();
      }
    } else if (e.key === 'Escape') {
      await clearSelectedAddreses();
      // Hide the dropdown
      hideDropdown();
    }
    // Exit the function so we don't end up seraching the database
    return;
  }
  // We get search suggestions from the API but we don't want to overwhelm it
  // So we debounce the requests
  clearTimeout(searchTimeOut);
  searchTimeOut = setTimeout(async () => {
    const address = e.target.value;
    if (address.length > 3) {
      // Only search if we have at least three character
      try {
        res = await axios.get('/search/suggest', { params: { address } });
        if (res.data.success) {
          updateAddressDropdown(res.data.data.suggestions);
        }
      } catch (error) {
        console.log('Error getting suggestions', error);
      }
    } else {
      hideDropdown();
    }
  }, 400);
});

/*
 * Show the dropdown, gets called if the dropdown has any values
 * */
function showDropdown() {
  addressDropdown.classList.add('show');
}

/*
 * Hide the dropdown, gets called if there is a selection of the operation is canceled
 * */
function hideDropdown() {
  addressDropdown.classList.remove('show');
}

/*
 * Mark an address as selected in the dropdown
 * */
function updateAddressSelection() {
  Array.from(addressDropdown.children).forEach((item, index) => {
    const link = item.firstChild;
    if (index === selectedAddressIndex) {
      link.classList.add('active');
      link.scrollIntoView({ block: 'nearest' });
    } else {
      link.classList.remove('active');
    }
  });
}

/*
 * Create the dropdown menu based on suggestions
 * */
function updateAddressDropdown(suggestions) {
  // Clear the suggestions
  addressDropdown.innerHTML = '';
  selectedAddressIndex = -1;

  if (suggestions.length === 0) {
    // We did not get any suggestions, hide the dropdown and exit
    hideDropdown();
    return;
  }

  suggestions.forEach((suggestion) => {
    if (suggestion.feature_type === 'place') {
      // We ignore places since there doesn't seem to be a way to tell
      // the api to ignore them
      return;
    }
    // Create the item
    const item = document.createElement('li');
    const link = document.createElement('a');
    link.className = 'dropdown-item';
    link.href = '#';
    link.textContent = `${suggestion.name}, ${suggestion.place_formatted}`;
    link.dataset.mapboxId = suggestion.mapbox_id;

    // The link has a mouse over event so it'll highlight the selection
    link.addEventListener('mouseenter', () => {
      selectedAddressIndex = Array.from(addressDropdown.children).indexOf(item);
      updateAddressSelection();
    });

    // And a click even to actually select the item
    link.addEventListener('click', async (e) => {
      e.preventDefault();
      addressField.value = `${suggestion.name}, ${suggestion.place_formatted}`;
      addressField.dataset.mapboxId = suggestion.mapbox_id;
      await clearSelectedAddreses();

      hideDropdown();
    });

    // Add the link to the item
    item.appendChild(link);
    // Add the item to the drowpdown
    addressDropdown.append(item);
  });
  showDropdown();
}

/*
 * Clear the selected address in the saved addresses section, so that the field
 * is the one that runs
 * */
async function clearSelectedAddreses() {
  // TODO: this is duplicate code, combine it witl app_control

  // Remove active class from all items
  document.querySelectorAll('.saved-address').forEach((item) => {
    item.children[1].children[0].innerText = 'Select';
    item.classList.remove('active');
  });
}
