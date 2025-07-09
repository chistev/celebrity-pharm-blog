function submitForm(event) {
    event.preventDefault();
    const form = document.getElementById("newsletter-form");
    const button = form.querySelector("button[type='submit']");
    const formData = new FormData(form);

    // Disable and grey out the button
    button.disabled = true;
    button.classList.add("opacity-50", "cursor-not-allowed");

    fetch("/subscribe/", { // You can use {% url 'subscribe' %} in the template
        method: "POST",
        headers: {
            "X-CSRFToken": formData.get("csrfmiddlewaretoken")
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Check your email to confirm your subscription.");
            form.reset();
        } else {
            alert(data.error || "Something went wrong.");
        }
    })
    .catch(error => {
        console.error("Subscription error:", error);
        alert("An error occurred. Please try again later.");
    })
    .finally(() => {
        // Re-enable the button
        button.disabled = false;
        button.classList.remove("opacity-50", "cursor-not-allowed");
    });
}
