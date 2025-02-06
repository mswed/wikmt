/*
 ****************************************************************************************************************************
 * RECENT SEARCHES
 * **************************************************************************************************************************
 */

document.querySelectorAll('.recent-search-select').forEach((button) => {
  button.addEventListener('click', (evt) => {
    evt.preventDefault();
    selectSearch(button);
  });
});

/* Select a search from the searches list
 * @param {object} element - the button that was clicked
 * */
async function selectSearch(element) {
  document.querySelectorAll('.card.list-group-item').forEach((item) => {
    item.classList.remove('active');
  });
  element.classList.add('active');
  const searchId = element.dataset.searchId;
  const searchData = await axios.post('/load/search', { searchId });
  if (searchData.data.success) {
    console.log('Got search!', searchData.data.success);
    const data = searchData.data.success;
    const [wwtpStats, county] = await performSearch(data.address, data.mapboxId, data.startDate, data.endDate);
    displayResults(data.startDate, data.endDate, data.address, data.mapboxId, county, wwtpStats);
  }
}
