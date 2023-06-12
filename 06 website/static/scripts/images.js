function displayImage(image) {
    const selectedImage = document.getElementById("selected-image");
    const imageMetadata = document.getElementById("image-metadata");

    selectedImage.src = image.url;
    selectedImage.alt = "Selected Image";
    selectedImage.classList.add("selected-image-class");
    imageMetadata.innerHTML = `
        <h2>Location: ${image.latitude}, ${image.longtitude}</h2>
        <h2>Picture taken at: ${image.date}</h2>
    `;
}

