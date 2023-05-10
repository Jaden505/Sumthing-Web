async function updateSelectedImage(img) {
    document.getElementById('selected-image').src = img.src;
    console.log(img.src)

    console.log(await getCurrentWeatherData("52.374_4.890"))
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

