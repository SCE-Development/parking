const currentDate = new Date();
const month = (currentDate.getMonth() + 1).toLocaleString('en-US', { minimumIntegerDigits: 2, useGrouping: false });
const day = currentDate.getDate().toLocaleString('en-US', { minimumIntegerDigits: 2, useGrouping: false });

console.log(`Current Date: ${month}/${day}`);