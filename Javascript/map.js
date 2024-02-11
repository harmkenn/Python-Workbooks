// Load map library
const map = L.map('map').setView([0, 18], 2); // Center on Africa with zoom level 2

// Load map tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Load country borders and population data
fetch('world_population.geojson')
  .then(response => response.json())
  .then(data => {
    // Process data, create color scale, and add choropleth layer
    L.geoJson(data, {
      style: (feature) => {
        // Define style based on population and color scale
      }
    }).addTo(map);
  });
