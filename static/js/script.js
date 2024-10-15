function fetchSolarWind() {
    fetch(`/solar_wind?t=${new Date().getTime()}`)
        .then(response => response.json())
        .then(data => {
            if (!data.error) {
                document.getElementById('solar_wind').innerText = `Solar Wind Speed: ${data.wind_speed} km/sec;  Bt: ${data.bt} nT, Bz: ${data.bz} nT`;
            } else {
                console.error('Failed to fetch content:', data.error);
            }
        })
        .catch(error => console.error('Error:', error));
}

function fetchKpImage() {
    fetch(`/Kp_image?t=${new Date().getTime()}`)
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
}

function fetchPlasma() {
    fetch(`/plasma?t=${new Date().getTime()}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('speedImage').src = data.speed_image;
            document.getElementById('densityImage').src = data.density_image;
            document.getElementById('temperatureImage').src = data.temperature_image;
        })
        .catch(error => console.error('Error fetching images:', error));
}

function fetchMag() {
    fetch(`/mag?t=${new Date().getTime()}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('BtBzImage').src = data.mag_image;
            document.getElementById('phiImage').src = data.phi_image;
            document.getElementById('aeImage').src = data.ae_image;
        })
        .catch(error => console.error('Error fetching images:', error));
}

function fetchForecast() {
    fetch(`/3-day forecast?t=${new Date().getTime()}`)
        .then(response => response.text())
        .then(data => {
            document.getElementById('forecastContent').textContent = data;
        })
        .catch(error => {
            document.getElementById('forecastContent').textContent = 'Error loading forecast';
            console.error('Error fetching the forecast:', error);
        });
}

function fetchOverview() {
    fetch(`/overview?t=${new Date().getTime()}`)
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
}

function fetchHUXt() {
    fetch(`/huxt?t=${new Date().getTime()}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('HUXtImage').src = data.huxt_image;
        })
        .catch(error => console.error('Error fetching images:', error));
}

function fetchLocation() {
    fetch(`/location?t=${new Date().getTime()}`)
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
}

function loadLASCO(){
    document.getElementById("LascoC2").src = `http://127.0.0.1:5000/stream_lascoc2?t=${new Date().getTime()}`
    document.getElementById("LascoC3").src = `http://127.0.0.1:5000/stream_lascoc3?t=${new Date().getTime()}`
}

function loadWSA(){
    document.getElementById("WSA").src = `http://127.0.0.1:5000/stream_wsa-enlil?t=${new Date().getTime()}`
}

function loadAURORA(){
    document.getElementById("AURORA").src = `http://127.0.0.1:5000/stream_aurora?t=${new Date().getTime()}`;
    fetch(`/aurora?t=${new Date().getTime()}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('AURORA_pic').src = data.aurora_image;
        })
        .catch(error => console.error('Error fetching images:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    const tocLinks = document.querySelectorAll('#toc a');
    const collapsibles = document.querySelectorAll('.collapsible');

    collapsibles.forEach(function(collapsible) {
        const content = collapsible.nextElementSibling;

        collapsible.addEventListener('click', function() {
            this.classList.toggle('active');
            var content = this.nextElementSibling;
            if (content.style.maxHeight) {
                content.style.maxHeight = null;
            } else {
                content.style.maxHeight = content.scrollHeight + "px";
            }
        });

        const images = content.querySelectorAll('img');
        images.forEach(image => {
            image.addEventListener('load', () => {
                if (collapsible.classList.contains('active')) {
                    content.style.maxHeight = content.scrollHeight + "px";
                }
            });
        });
    });

    tocLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetID = this.getAttribute('href').trim();

            try {
                const targetElement = document.querySelector(targetID);

                let sectionElement = targetElement.closest('.collapsible');
                if (!sectionElement) {
                    sectionElement = targetElement.closest('.content')?.previousElementSibling;
                }

                if (sectionElement && sectionElement.classList.contains('collapsible') && !sectionElement.classList.contains('active')) {
                    sectionElement.click();
                }

                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            } catch (error) {
                console.error("Error selecting target element:", error);
            }
        });
    });


});



fetchSolarWind();
fetchKpImage();
fetchPlasma();
fetchMag();
fetchForecast();
fetchOverview();
fetchHUXt();
fetchLocation();
loadAURORA();
loadLASCO();
loadWSA();

const min = 1000*60;
setInterval(fetchSolarWind, 1*min);
setInterval(fetchKpImage, 30*min);
setInterval(fetchPlasma, 10*min);
setInterval(fetchMag, 10*min);
setInterval(fetchForecast, 180*min);
setInterval(fetchOverview, 60*min);
setInterval(fetchHUXt, 30*min);
setInterval(loadAURORA, 30*min);
setInterval(loadLASCO, 120*min);
setInterval(loadWSA, 60*min)