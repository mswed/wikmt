function showToast(message, title = 'Message', type = 'info') {
  const toast = document.getElementById('messageToast');
  const toastTitle = document.getElementById('toastTitle');
  const toastMessage = document.getElementById('toastMessage');

  toast.classList.remove('bg-success', 'bg-danger', 'bg-warning', 'bg-info');
  toast.classList.add(`bg-${type}`);

  toastTitle.innerText = title;
  toastMessage.innerText = message;

  const bsToast = new bootstrap.Toast(toast);
  bsToast.show();
}

/*
 * Format a date into Month day, Year
 * @param {string} date - date to format
 * @returns {string} - formatted date (Ap 2, 2013)
 * */
function formatDate(date) {
  const dateObj = new Date(date);
  return dateObj.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

/*
 * Format a number to comma-format
 * @param {string} num - number to format
 * @returns {string} - formatted nunmber (1,000)
 * */
function formatNumber(number) {
  num = +number;
  return num.toLocaleString('en-US');
}
