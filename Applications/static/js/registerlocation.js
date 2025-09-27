document.addEventListener('DOMContentLoaded', () => {
    const location = document.getElementById('location');

    const LocationArray = ['A', 'B', 'C', 'D', 'E', 'F', 'Z','Y', 'X', 'W', 'V', 'U'];

    LocationArray.forEach(loc => {
        const option = document.createElement('option')
        option.value = loc;
        option.textContent = loc;
        location.appendChild(option);
    });
});