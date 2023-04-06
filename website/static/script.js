function updateSelectedImage(img) {
    document.getElementById('selected-image').src = img.src;
}

function handleScroll(event) {
    event.preventDefault();
    const scrollAmount = event.deltaY;
    event.target.scrollBy({ left: scrollAmount, behavior: 'smooth' });
}
