function validateRegisterForm(data, errormessage) {
    const usernamePattern = /^[a-zA-Z0-9_]+$/;

    // Name
    if (!data.name.trim()) {
        errormessage.style.display = 'block';
        errormessage.textContent = "Name is required.";
        errormessage.style.color = 'red';
        console.log("name missing");
        return false;
    }

    // Username
    if (!data.username.trim()) {
        errormessage.style.display = 'block';
        errormessage.textContent = "Username is required.";
        errormessage.style.color = 'red';
        console.log("username missing");
        return false;
    }
    if (!usernamePattern.test(data.username)) {
        errormessage.style.display = 'block';
        errormessage.textContent = "Username can only contain letters, numbers, and underscores.";
        errormessage.style.color = 'red';
        return false;
    }

    // Password
    if (!data.password.trim()) {
        errormessage.style.display = 'block';
        errormessage.textContent = "Password is required.";
        errormessage.style.color = 'red';
        console.log("password missing");
        return false;
    }
    if (data.password.length < 6) {
        errormessage.style.display = 'block';
        errormessage.textContent = "Password must be at least 6 characters.";
        errormessage.style.color = 'red';
        return false;
    }

    // Location
    if (!data.location.trim()) {
        errormessage.style.display = 'block';
        errormessage.textContent = "Location is required.";
        errormessage.style.color = 'red';
        console.log("location missing");
        return false;
    }

    errormessage.style.display = 'none';
    return true;
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('register-section');
    const errormessage = document.getElementById('error-msg');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const data = {
            name: document.getElementById('name').value,
            username: document.getElementById('register-username').value,
            password: document.getElementById('register-password').value,
            location: document.getElementById('location').value,
        };

        if (!validateRegisterForm(data, errormessage)) {
            return;
        }

        const API = '/create';

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
                    setTimeout(() => {
                        window.location.pathname = '/login';
                    }, 500);
                    break;

                case 400:
                case 409:
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