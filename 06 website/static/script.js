async function updateSelectedImage(img) {
    document.getElementById('selected-image').src = img.src;


    let original_img_src = img.src
    let url_to_remove = "http://127.0.0.1:5000/static/images/"
    let img_name = original_img_src.replace(url_to_remove, '')

    const imageData = await getImageData(img_name);

    const weatherForecastTable = document.querySelector(".weather-forecast-table");
    const weatherInfoSection = document.querySelector(".weather-info");

    if (imageData[0] === undefined) {
        weatherForecastTable.style.display = "none"
        // Clear table content, if previous image had data
        weatherForecastTable.innerHTML = ""
    } else {
        weatherForecastTable.style.display = "block"
        weatherInfoSection.style.display = "block"

        const forecastData = await getWeatherForecast(imageData[0].latitude, imageData[0].longitude)
        buildWeatherForecastTable(forecastData);
    }
}

function handleScroll(event) {
    event.preventDefault();
    const scrollAmount = event.deltaY;
    event.target.scrollBy({left: scrollAmount, behavior: 'smooth'});
}


async function getCurrentWeatherData(query) {
    const api_key = "2b4a3252534e0a5ccd7a7baef67120a3";
    const xhr = new XMLHttpRequest();
    xhr.open('GET', 'http://api.weatherstack.com/current?access_key=' + api_key + `&query=${query}`, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            return xhr.responseText
            // Process the response here
        }
    };
    xhr.send();
}

async function getWeatherForecast(latitude, longitude) {
    const response = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&hourly=temperature_2m`);

    const date = new Date();

    const currentDate = date.toISOString().slice(0, 10);

    date.setDate(date.getDate() + 2);
    const futureDate = date.toISOString().slice(0, 10);
    const responseData = await response.json();

    // Extract the hourly temperature data
    const hourlyTemperature = responseData.hourly.temperature_2m;

    // Extract the hourly time data
    const hourlyTime = responseData.hourly.time;

    // Get the indices for the desired date range (from May 15th to May 15th)
    const startDate = new Date(currentDate + 'T00:00');
    const endDate = new Date(currentDate + 'T23:00');

    const startIndex = hourlyTime.findIndex(time => new Date(time) >= startDate);
    const endIndex = hourlyTime.findIndex(time => new Date(time) > endDate) - 1;


    // Slice the arrays to get the data for the desired date range
    const hourlyTemperatureRange = hourlyTemperature.slice(startIndex, endIndex + 1);
    const hourlyTimeRange = hourlyTime.slice(startIndex, endIndex + 1);

    // Combine the temperature and time data into an array of objects
    return hourlyTemperatureRange.map((temperature, index) => ({
        time: hourlyTimeRange[index],
        temperature,
        readable_time: new Date(hourlyTimeRange[index]).toLocaleDateString() + " " + new Date(hourlyTimeRange[index]).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit"
        })
    }));
}

/**
 * Creates the weather forecast table
 * @param data
 */
function buildWeatherForecastTable(data) {
    // Create the table element
    let table = document.createElement('table');

    // Create the table header
    let thead = document.createElement('thead');
    let headerRow = document.createElement('tr');
    let timeHeaderCell = document.createElement('th');
    let temperatureHeaderCell = document.createElement('th');
    timeHeaderCell.textContent = 'Time';
    temperatureHeaderCell.textContent = 'Temperature';
    headerRow.appendChild(timeHeaderCell);
    headerRow.appendChild(temperatureHeaderCell);
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Create the table body
    let tbody = document.createElement('tbody');
    for (let i = 0; i < data.length; i++) {
        let row = document.createElement('tr');
        let timeCell = document.createElement('td');
        let temperatureCell = document.createElement('td');
        timeCell.textContent = data[i].readable_time;
        temperatureCell.textContent = data[i].temperature + ' °C';
        row.appendChild(timeCell);
        row.appendChild(temperatureCell);
        tbody.appendChild(row);
    }
    table.appendChild(tbody);

    // Clear the weatherData div
    let weatherDataDiv = document.querySelector('.weather-forecast-table');
    weatherDataDiv.innerHTML = '';

    // Append the table to the weatherData div
    weatherDataDiv.appendChild(table);
}


/**
 * Retrieves image data by calling the API
 * @param img_name - image name
 * @returns {Promise<void>} - data of the image
 */
async function getImageData(img_name) {
    const response = await fetch(`http://127.0.0.1:5000/get_image_data?query=${img_name}`);
    return await response.json();
}

