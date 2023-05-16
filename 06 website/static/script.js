async function updateSelectedImage(img) {
    document.getElementById('selected-image').src = img.src;


    let original_img_src = img.src
    let url_to_remove = window.location.href + "static/images/"
    let img_name = original_img_src.replace(url_to_remove, '')

    const imageData = await getImageData(img_name);
    const image = imageData[0];

    const weatherForecastChart = document.querySelector("#weatherChart");
    const weatherInfoSection = document.querySelector(".weather-info");

    if (image === undefined) {
        weatherForecastChart.style.display = "none"
        // Clear table content, if previous image had data

    } else {
        // weatherForecastTable.style.display = "block"
        weatherInfoSection.style.display = "block"

        const date = new Date(image.img_creation_date)
        const dateFormatted = date.toISOString().slice(0, 10);

        const historicalData = await getHistoricalWeatherData(image.latitude, image.longitude, dateFormatted)
        console.log(historicalData)
        buildWeatherGraph(historicalData);
    }
}

function handleScroll(event) {
    event.preventDefault();
    const scrollAmount = event.deltaY;
    event.target.scrollBy({left: scrollAmount, behavior: 'smooth'});
}

async function getHistoricalWeatherData(latitude, longitude, date) {
    const response = await fetch(`https://archive-api.open-meteo.com/v1/archive?latitude=${latitude}&longitude=${longitude}&start_date=${date}&end_date=${date}&hourly=temperature_2m,rain`);

    const imageDate = new Date(date);
    const currentDate = imageDate.toISOString().slice(0, 10);

    const responseData = await response.json();

    const hourlyTemperature = responseData.hourly.temperature_2m;
    const hourlyTime = responseData.hourly.time;
    const hourlyRain = responseData.hourly.rain;

    const hourlyTemperatureUnit = responseData.hourly_units.temperature_2m;
    const hourlyRainUnit = responseData.hourly_units.rain;

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
    const hourlyRainRange = hourlyRain.slice(startIndex, endIndex + 1);

    // Combine the temperature and time data into an array of objects
    return hourlyTemperatureRange.map((temperature, index) => ({
        time: hourlyTimeRange[index],
        rain: hourlyRainRange[index],
        temperature,
        temperature_unit: hourlyTemperatureUnit,
        rain_unit: hourlyRainUnit,
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

    const labels = data.map(entry => entry.readable_time);
    const temperatures = data.map(entry => entry.temperature);
    const rain = data.map(entry => entry.rain);

    const temperatureUnit = data[0].temperature_unit;
    const rainUnit = data[0].rain_unit;


    // Create a new chart instance
    const ctx = document.querySelector('#weatherChart').getContext('2d');

    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: `Temperature (${temperatureUnit})`,
                    data: temperatures,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                },
                {
                    label: `Rain (${rainUnit})`,
                    data: rain,
                    backgroundColor: 'rgba(45, 85, 255, 0.2)',
                    borderColor: 'rgba(45, 85, 255, 1)',
                    borderWidth: 1
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

