import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { useEffect, useState } from 'react';
import 'leaflet-routing-machine';

// Arreglar íconos
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const ESPE = { lat: -0.33405, lng: -78.45217 };

const cajeros = [
  { nombre: 'San Luis', lat: -0.30828, lng: -78.45077 },
  { nombre: 'Av Luis Cordero', lat: -0.32733, lng: -78.44646 },
  { nombre: 'Av General Enríquez', lat: -0.32771, lng: -78.45037 },
  // ...otros cajeros
];

const MapaCajeros = () => {
  const [cajeroMasCercano, setCajeroMasCercano] = useState(null);

  useEffect(() => {
    let minDistancia = Infinity;
    let cercano = null;

    cajeros.forEach((cajero) => {
      const url = `https://router.project-osrm.org/route/v1/driving/${ESPE.lng},${ESPE.lat};${cajero.lng},${cajero.lat}?overview=false`;

      fetch(url)
        .then((res) => res.json())
        .then((data) => {
          const distancia = data.routes?.[0]?.distance || Infinity;
          console.log(`${cajero.nombre}: ${distancia.toFixed(2)} m`);

          if (distancia < minDistancia) {
            minDistancia = distancia;
            cercano = cajero;
            setCajeroMasCercano(cajero);
          }
        })
        .catch((err) => {
          console.error(`Error con ${cajero.nombre}:`, err);
        });
    });
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

        <Marker position={[ESPE.lat, ESPE.lng]}>
          <Popup>ESPE Sangolquí</Popup>
        </Marker>

        {cajeros.map((cajero, idx) => (
          <Marker
            key={idx}
            position={[cajero.lat, cajero.lng]}
            icon={
              cajeroMasCercano?.nombre === cajero.nombre
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
              {cajeroMasCercano?.nombre === cajero.nombre && (
                <strong> (Más cercano)</strong>
              )}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};

export default MapaCajeros;
