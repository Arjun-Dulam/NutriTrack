

    let countdown = 5;
    const timerElement = document.getElementById('timer');
    const interval = setInterval(() => {
        countdown--;
        timerElement.textContent = countdown;
        if (countdown <= 0) {
            clearInterval(interval);
            window.location.href = redirectUrl;
        }
    }, 1000);