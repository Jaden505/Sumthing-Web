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


