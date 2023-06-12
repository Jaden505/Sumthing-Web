
async function getHistoricalWeatherData(latitude, longitude, date) {
    console.log(latitude, longitude, date)
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

    let labels = data.map(entry => entry.readable_time);
    labels = labels.map(label => label.split(' ')[1]);  // Only keep the time
    const temperatures = data.map(entry => entry.temperature);
    const rain = data.map(entry => entry.rain);

    const temperatureUnit = data[0].temperature_unit;
    const rainUnit = data[0].rain_unit;

    const ctx = document.querySelector('#weatherChart').getContext('2d');

    // Define the dataset options for the temperature dataset
    const temperatureDatasetOptions = {
        label: `Temperature (${temperatureUnit})`,
        data: temperatures,
        backgroundColor: 'rgba(192, 75, 75, 0.2)',
        borderColor: 'rgba(192, 75, 75, 1)',
        borderWidth: 1,
    };

    // Define the dataset options for the rain dataset
    const rainDatasetOptions = {
        label: `Rain (${rainUnit})`,
        data: rain,
        backgroundColor: 'rgba(45, 85, 255, 0.2)',
        borderColor: 'rgba(45, 85, 255, 1)',
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
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                },
                x: {
                    position: 'top'
                }
            },
        },
    });
}
