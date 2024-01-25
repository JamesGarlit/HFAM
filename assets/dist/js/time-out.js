let scanner = new Instascan.Scanner({ video: document.getElementById('scanner') });
    let loggedInUser = '{{ request.user.get_full_name }}'; // Replace this with the actual way you store the logged-in user's full name

    scanner.addListener('scan', function (content) {
        handleQRCode(content);
    });

    Instascan.Camera.getCameras().then(function (cameras) {
        if (cameras.length > 0) {
            scanner.start(cameras[0]);
        } else {
            toastr.error('No cameras found.');
        }
    }).catch(function (e) {
        toastr.error(e);
    });

    function handleQRCode(content) {
        // Assuming the QR code content is in the format 'firstname lastname | date'
        const [qrFullName, qrDate] = content.split(' | ');

        // Extract first and last names
        const [qrFirstName, qrLastName] = qrFullName.split(' ');

        // Get the current date in the Philippines timezone (Asia/Manila)
        let currentDate = new Date(new Date().toLocaleString("en-US", {timeZone: "Asia/Manila"}));

        // Format the current date to 'YYYY-MM-DD'
        let year = currentDate.getFullYear();
        let month = (currentDate.getMonth() + 1).toString().padStart(2, '0');
        let day = currentDate.getDate().toString().padStart(2, '0');
        let currentDateFormatted = `${year}-${month}-${day}`;

        console.log('QR Date:', qrDate);
        console.log('Current Date:', currentDateFormatted);

        // Check if the QR code date is the current date and the username matches the logged-in user
        if (qrDate === currentDateFormatted && qrFirstName === loggedInUser.split(' ')[0] && qrLastName === loggedInUser.split(' ')[1]) {
            console.log('Valid QR code.');

            // Update the input fields with username and date information

            // Get current location and date
            navigator.geolocation.getCurrentPosition(async function (position) {
                const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${position.coords.latitude}&lon=${position.coords.longitude}`);
                const data = await response.json();
            
                // Extracting relevant parts excluding postcode and country
                const addressArray = data.display_name.split(',').slice(0, -4);
                const formattedAddress = addressArray.join(',');
            
                document.getElementById('location').value = formattedAddress.trim();
            });
            

            // Get current time
            let hours = currentDate.getHours().toString().padStart(2, '0');
            let minutes = currentDate.getMinutes().toString().padStart(2, '0');

            let timeFormatted = `${hours}:${minutes}`;

            document.getElementById('date').value = currentDateFormatted;
            document.getElementById('time_out').value = timeFormatted;
        } else {
            toastr.error('Invalid QR code.');
        }
    }