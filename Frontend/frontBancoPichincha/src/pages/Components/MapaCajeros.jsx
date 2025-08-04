import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { useState, useEffect } from 'react';

// Arregla iconos (Leaflet no carga bien los íconos por defecto en React)
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const ESPE = { lat: -0.3275504, lng: -78.4429118 };

const cajeros = [
  { nombre: 'San luis', lat: -0.30828, lng: -78.45077 },
  { nombre: 'Av Luis Cordero', lat: -0.32733, lng: -78.44646 },
  { nombre: 'Av General Enriques', lat: -0.32771, lng: -78.45037 },
  {
    nombre: 'Av Gral Rumiñahui Kywi San Rafael',
    lat: -0.30212,
    lng: -78.45626,
  },
  { nombre: 'Av. Río Curaray e Ilaló', lat: -0.29504, lng: -78.45199 },
  { nombre: 'Centro comercial Alondras', lat: -0.29012, lng: -78.44556 },
  { nombre: 'El triángulo - Pharmacys', lat: -0.30031, lng: -78.4604 },
  { nombre: 'Plaza del Valle', lat: -0.30016, lng: -78.45978 },
  { nombre: 'Av Gral Rumiñahui Isla Pinta', lat: -0.30623, lng: -78.44963 },
  { nombre: 'Av Luis Cordero', lat: -0.32728, lng: -78.44639 },
  { nombre: 'River Mall', lat: -0.32415, lng: -78.44891 },
  { nombre: 'Puente 9 - Papeleria', lat: -0.29095, lng: -78.46586 },
];

// Función para calcular distancia entre dos puntos geográficos en metros (Haversine)
function calcularDistancia(lat1, lon1, lat2, lon2) {
  const R = 6371e3; // Radio de la Tierra en metros
  const toRad = (x) => (x * Math.PI) / 180;

  const φ1 = toRad(lat1);
  const φ2 = toRad(lat2);
  const Δφ = toRad(lat2 - lat1);
  const Δλ = toRad(lon2 - lon1);

  const a =
    Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
    Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  const distancia = R * c; // en metros
  return distancia;
}

const MapaCajeros = () => {
  const [cajeroMasCercano, setCajeroMasCercano] = useState(null);

  useEffect(() => {
    let minDistancia = Infinity;
    let cercano = null;
    for (const cajero of cajeros) {
      const distancia = calcularDistancia(
        ESPE.lat,
        ESPE.lng,
        cajero.lat,
        cajero.lng
      );
      if (distancia < minDistancia) {
        minDistancia = distancia;
        cercano = cajero;
      }
    }
    setCajeroMasCercano(cercano);
  }, []);

  return (
    <div className="mt-10 rounded-lg overflow-hidden shadow border border-gray-300">
      <h2 className="text-xl font-bold text-blue-900 mb-4 px-4 pt-4">
        Cajeros Banco Pichincha cerca de ESPE Sangolquí
      </h2>
      <MapContainer
        center={[ESPE.lat, ESPE.lng]}
        zoom={14}
        style={{ height: '450px', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Marcador de la ESPE */}
        <Marker position={[ESPE.lat, ESPE.lng]}>
          <Popup>ESPE Sangolquí (Referencia)</Popup>
        </Marker>

        {/* Marcadores cajeros */}
        {cajeros.map((cajero, idx) => (
          <Marker
            key={idx}
            position={[cajero.lat, cajero.lng]}
            // Cambiamos color del icono para el cajero más cercano
            icon={
              cajeroMasCercano && cajero.nombre === cajeroMasCercano.nombre
                ? new L.Icon({
                    iconUrl:
                      'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
                    shadowUrl:
                      'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41],
                  })
                : new L.Icon.Default()
            }
          >
            <Popup>
              {cajero.nombre}
              {cajeroMasCercano &&
                cajero.nombre === cajeroMasCercano.nombre && (
                  <div>
                    <strong> (Más cercano a ESPE) </strong>
                  </div>
                )}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};

export default MapaCajeros;
