async function updateSelectedImage(img) {
    document.getElementById('selected-image').src = img.src;


    let original_img_src = img.src
    let url_to_remove = "http://127.0.0.1:5000/static/images/"
    let img_name = original_img_src.replace(url_to_remove, '')

    await getImageData(img_name)
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

/**
 * Retrieves image data by calling the API
 * @param img_name - image name
 * @returns {Promise<void>} - data of the image
 */
async function getImageData(img_name) {
    const response = await fetch(`http://127.0.0.1:5000/get_image_data?query=${img_name}`);
    const jsonData = await response.json();
    console.log(jsonData);
}

