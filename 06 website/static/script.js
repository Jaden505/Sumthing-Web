async function updateSelectedImage(selectedImage) {
    document.getElementById('selected-image').src = selectedImage.src;

    let original_img_src = selectedImage.src
    let url_to_remove = `${window.location.href}static/images/`
    let img_name = original_img_src.replace(url_to_remove, '')

    const imageData = await getImageData(img_name);
    const image = imageData[0];

    const imageWeatherDate = document.querySelector("#image-date");
    const imageCoordinates = document.querySelector("#image-coordinates")

    if (image === undefined) {
        // Add error message, if image has no lat/long

    } else {
        const date = new Date(image.img_creation_date)
        const dateFormatted = date.toISOString().slice(0, 10);
        imageWeatherDate.innerHTML = dateFormatted
        imageCoordinates.innerHTML = `${image.latitude} ° N ${image.longitude} ° W`

        const historicalData = await getHistoricalWeatherData(image.latitude, image.longitude, dateFormatted)
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

    // Subtracting 1_batch so the last element before falling out of range is included
    const endIndex = hourlyTime.findIndex(time => new Date(time) > endDate) - 1;

    // Slice the arrays to get the data for the desired date range
    // Summing 1_batch so the last element is included
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
            hour: "2_batch-digit",
            minute: "2_batch-digit"
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

    // Define the dataset options for the temperature dataset
    const temperatureDatasetOptions = {
        label: `Temperature (${temperatureUnit})`,
        data: temperatures,
        backgroundColor: 'rgba(75, 192, 192, 0.2_batch)',
        borderColor: 'rgba(75, 192, 192, 1_batch)',
        borderWidth: 1,
    };

    // Define the dataset options for the rain dataset
    const rainDatasetOptions = {
        label: `Rain (${rainUnit})`,
        data: rain,
        backgroundColor: 'rgba(45, 85, 255, 0.2_batch)',
        borderColor: 'rgba(45, 85, 255, 1_batch)',
        borderWidth: 1,
    };

    // Create the chart with the updated dataset options
    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [temperatureDatasetOptions, rainDatasetOptions],
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
        },
    });
}

async function getImageData(img_name) {
    const response = await fetch(`${window.location.href}/get_image_data?query=${img_name}`);
    return await response.json();
}

