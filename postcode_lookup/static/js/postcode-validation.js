function validate(js_strings) {
    // Get the postcode input element
    const postcodeInput = document.getElementById('postcode-search');
    const error_message = js_strings.postcode_input_error_message;
    // Function to set custom validity message
    postcodeInput.addEventListener('invalid', function (event) {
        if (postcodeInput.validity.patternMismatch) {
            postcodeInput.setCustomValidity(error_message);
        } else if (postcodeInput.validity.valueMissing) {
            postcodeInput.setCustomValidity(error_message);
        } else {
            postcodeInput.setCustomValidity(''); // Clear custom messages if no pattern mismatch
        }
    });

    // Clear custom validity message on input
    postcodeInput.addEventListener('input', function () {
        postcodeInput.setCustomValidity('');
    });


    // Function to get query parameter value by name
    function getQueryParam(param) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(param);
    }

    // Function to handle error message display
    function handleErrorDisplay(param, message = null) {
        if (getQueryParam(param) === '1') {
            // display error message
            document.getElementById('dc-postcode-search-form').classList.add("error");
            postcodeInput.setAttribute("aria-invalid", "true");
            // optionally customize message text
            if (message) {
                document.getElementById('postcode-search-error-message').innerHTML = message;
            }
        }
    }

    handleErrorDisplay('invalid-postcode');
    handleErrorDisplay('api-error', "Sorry, there's a problem with this service at the moment. We're working to fix it as soon as possible.");

    postcodeInput.addEventListener('input', function () {
        if (postcodeInput.validity.valid) {
            postcodeInput.setAttribute("aria-invalid", "false");
        }

    })
}
