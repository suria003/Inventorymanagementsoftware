function Validator(data, errormessage) {
    const usernamePattern = /^[a-zA-Z0-9_]+$/;

    if (!data.username.trim()) {
        errormessage.style.display = 'block';
        errormessage.textContent = "Username is required.";
        errormessage.style.color = 'red';
        return false;
    }
    
    if (!usernamePattern.test(data.username)) {
        errormessage.style.display = 'block';
        errormessage.textContent = "Username can only contain letters, numbers, and underscores.";
        errormessage.style.color = 'red';
        return false;
    }

    if (!data.password.trim()) {
        errormessage.style.display = 'block';
        errormessage.textContent = "Password is required.";
        errormessage.style.color = 'red';
        return false;
    }

    errormessage.style.display = 'none';
    return true;
}

document.addEventListener('DOMContentLoaded', () => {

    const form = document.getElementById('login-section');
    const errormessage = document.getElementById('error-msg');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const data = {
            username: document.getElementById('username').value,
            password: document.getElementById('password').value,
        };

        console.log(data);

        if (!Validator(data, errormessage)){
            return;
        }

        const API = 'http://127.0.0.1:3000/login';

        try {
            const response = await fetch(API, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            switch (response.status) {
                case 200:
                    errormessage.style.display = 'block';
                    errormessage.textContent = result.message || 'Login successful!';
                    errormessage.style.color = 'green';
                    setTimeout(() => {
                        window.location.pathname = '/';
                    }, 500);
                    break;

                case 400:
                case 401:
                case 404:
                    errormessage.style.display = 'block';
                    errormessage.textContent = result.message || 'Error occurred.';
                    errormessage.style.color = 'red';
                    break;

                default:
                    errormessage.style.display = 'block';
                    errormessage.textContent = 'Unexpected error, try again.';
                    errormessage.style.color = 'red';
                    break;
            }

        } catch (err) {
            errormessage.style.display = 'block';
            errormessage.textContent = 'Request failed: ' + err.message;
            errormessage.style.color = 'red';
        }
    });

});