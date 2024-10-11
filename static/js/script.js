fetch('/solar_wind')
    .then(response => response.json())
    .then(data => {
        if (!data.error) {
            document.getElementById('solar_wind').innerText = `Solar Wind Speed: ${data.wind_speed} km/sec;  Bt: ${data.bt} nT, Bz: ${data.bz} nT`;
        } else {
            console.error('Failed to fetch content:', data.error);
        }
    })
    .catch(error => console.error('Error:', error));

fetch('/Kp_image')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.blob();
        })
        .then(imageBlob => {
            const imageObjectURL = URL.createObjectURL(imageBlob);
            const kpImageElement = document.getElementById('kp_image');
            kpImageElement.src = imageObjectURL;
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });

fetch('/plasma')
        .then(response => response.json())
            .then(data => {
                document.getElementById('speedImage').src = data.speed_image;
                document.getElementById('densityImage').src = data.density_image;
                document.getElementById('temperatureImage').src = data.temperature_image;
            })
            .catch(error => console.error('Error fetching images:', error));

fetch('/mag')
        .then(response => response.json())
            .then(data => {
                document.getElementById('BtBzImage').src = data.mag_image;
                document.getElementById('phiImage').src = data.phi_image;
                document.getElementById('aeImage').src = data.ae_image;
            })
            .catch(error => console.error('Error fetching images:', error));

fetch('/3-day forecast')
    .then(response => response.text())
        .then(data =>{
            document.getElementById('forecastContent').textContent = data;
        }).catch(error => {
            document.getElementById('forecastContent').textContent = 'Error loading forecast';
            console.error('Error fetching the forecast:', error);
        });

fetch('/overview')
        .then(response => response.json())
        .then(data => {
            if (data.overview) {
                let content = '<ul>';
                data.overview.forEach(item => {
                    content += `<li>Date: ${item[0]}, ${item[1]}, ${item[2]}, ${item[3]}</li>`;
                });
                content += '</ul>';
                document.getElementById('overviewContent').innerHTML = content;
            } else {
                document.getElementById('overviewContent').textContent = 'No data available';
            }
        })
        .catch(error => {
            document.getElementById('overviewContent').textContent = 'Error loading data';
            console.error('Error fetching overview:', error);
        });

fetch('/huxt')
        .then(response => response.json())
            .then(data => {
                document.getElementById('HUXtImage').src = data.huxt_image;
            })
            .catch(error => console.error('Error fetching images:', error));

fetch('/location')
    .then(response => response.json())
    .then(data => {
        if (!data.error) {
            document.getElementById('lat_lon').innerText = `Latitude: ${data.latitude}, Longitude: ${data.longitude}`;
            document.getElementById('geo_lat').innerText = `Geomagnetic Latitude: ${data.geolatitude}`;
        } else {
            console.error('Failed to fetch content:', data.error);
        }
    })
    .catch(error => console.error('Error:', error));