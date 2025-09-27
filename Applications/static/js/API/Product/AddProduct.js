document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('product-form');
    const errormessage = document.getElementById('error-msg');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const data = {
            productname: document.getElementById('product-name').value,
            productprice: document.getElementById('product-price').value,
            productquantity: document.getElementById('product-quantity').value,
        };

        const API = 'http://127.0.0.1:3000/product';

        try {

            const response = await fetch(API, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            switch (response.status) {
                case 201:
                case 200:
                    errormessage.style.display = 'block';
                    errormessage.textContent = result.message;
                    errormessage.style.color = 'green';
                    window.location.pathname = '/product';
                    break;

                case 400:
                case 404:
                case 500:
                    errormessage.style.display = 'block';
                    errormessage.textContent = result.message;
                    errormessage.style.color = 'red';
                    break;

                default:
                    errormessage.style.display = 'block';
                    errormessage.textContent = result.message;
                    errormessage.style.color = 'red';
                    break;
            }
        } catch (err) {
            errormessage.style.display = 'block';
            errormessage.textContent = err.message;
            errormessage.style.color = 'red';
        }

    });
});