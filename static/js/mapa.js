/* Utilidades de mapa para TRAIBER: geocodificacion (Nominatim) y rutas (OSRM), ambos gratuitos. */

async function buscarDirecciones(texto) {
    if (!texto || texto.length < 3) return [];
    const url = `https://nominatim.openstreetmap.org/search?format=json&countrycodes=pe&addressdetails=0&limit=5&q=${encodeURIComponent(texto)}`;
    const respuesta = await fetch(url, { headers: { 'Accept-Language': 'es' } });
    if (!respuesta.ok) return [];
    return respuesta.json();
}

async function calcularRuta(origenLat, origenLng, destinoLat, destinoLng) {
    const url = `https://router.project-osrm.org/route/v1/driving/${origenLng},${origenLat};${destinoLng},${destinoLat}?overview=full&geometries=geojson`;
    const respuesta = await fetch(url);
    if (!respuesta.ok) return null;
    const datos = await respuesta.json();
    if (!datos.routes || !datos.routes.length) return null;
    const ruta = datos.routes[0];
    return {
        distanciaKm: ruta.distance / 1000,
        duracionMin: ruta.duration / 60,
        geojson: ruta.geometry,
    };
}

function configurarAutocompletado(inputEl, sugerenciasEl, alSeleccionar) {
    let temporizador = null;
    inputEl.addEventListener('input', () => {
        clearTimeout(temporizador);
        const texto = inputEl.value;
        temporizador = setTimeout(async () => {
            const resultados = await buscarDirecciones(texto);
            sugerenciasEl.innerHTML = '';
            resultados.forEach((r) => {
                const item = document.createElement('button');
                item.type = 'button';
                item.className = 'list-group-item list-group-item-action';
                item.textContent = r.display_name;
                item.addEventListener('click', () => {
                    inputEl.value = r.display_name;
                    sugerenciasEl.innerHTML = '';
                    alSeleccionar(parseFloat(r.lat), parseFloat(r.lon), r.display_name);
                });
                sugerenciasEl.appendChild(item);
            });
        }, 500);
    });
}
