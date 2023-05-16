async function updateSelectedImage(img) {
    document.getElementById('selected-image').src = img.src;


    let original_img_src = img.src
    let url_to_remove = "http://127.0.0.1:5000/static/images/"
    let img_name = original_img_src.replace(url_to_remove, '')

    const imageData = await getImageData(img_name);

    const weatherForecastChart = document.querySelector("#weatherChart");
    const weatherInfoSection = document.querySelector(".weather-info");

    if (imageData[0] === undefined) {
        weatherForecastChart.style.display = "none"
        // Clear table content, if previous image had data

    } else {
        // weatherForecastTable.style.display = "block"
        weatherInfoSection.style.display = "block"

        const forecastData = await getWeatherForecast(imageData[0].latitude, imageData[0].longitude)
        buildWeatherGraph(forecastData);
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

    // Get the indices for the desired date range
    const startDate = new Date(currentDate + 'T00:00');
    const endDate = new Date(currentDate + 'T23:00');

    const startIndex = hourlyTime.findIndex(time => new Date(time) >= startDate);

    // Subtracting 1 so the last element before falling out of range is included
    const endIndex = hourlyTime.findIndex(time => new Date(time) > endDate) - 1;

    // Slice the arrays to get the data for the desired date range
    // Summing 1 so the last element is included
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

let chartInstance = null;

function buildWeatherGraph(data) {
    // Destroy the existing chart if it exists
    if (chartInstance) {
        chartInstance.destroy();
    }
    // Extract the time and temperature data from the weather data
    const labels = data.map(entry => entry.readable_time);
    const temperatures = data.map(entry => entry.temperature);

    // Create a new chart instance
    const ctx = document.querySelector('#weatherChart').getContext('2d');

    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Temperature',
                    data: temperatures,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)', // Set the background color of the chart area
                    borderColor: 'rgba(75, 192, 192, 1)', // Set the line color
                    borderWidth: 1 // Set the line width in pixels
                }
            ]
        },
        options: {
            responsive: true, // Make the chart responsive
            scales: {
                y: {
                    beginAtZero: true // Start the y-axis from zero
                },
                x: {
                    position: 'top'
                }
            },
        }
    });
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

