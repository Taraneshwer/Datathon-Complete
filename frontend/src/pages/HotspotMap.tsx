import { useEffect, useRef, useState } from 'react';
import { useListHotspots, useListDistricts } from '@/api-client';

import { useIntel } from '../context/IntelContext';
import { PageTransition } from '../components/Motion';
import { MapContainer, TileLayer, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import 'leaflet.heat';

// Type definitions to fix leaflet.heat missing types if any
declare module 'leaflet' {
  function heatLayer(latlngs: Array<[number, number, number]>, options?: any): any;
}

// Component to handle heat layer
function HeatLayer({ points }: { points: Array<[number, number, number]> }) {
  const map = useMap();
  
  useEffect(() => {
    if (!points.length) return;
    
    // Create heat layer with specific light-theme gradients
    const layer = L.heatLayer(points, {
      radius: 25,
      blur: 15,
      maxZoom: 12,
      max: 1.0,
      gradient: {
        0.2: '#BFD0DE', // data-2
        0.4: '#8FAFC7', // data-3
        0.6: '#4F7A9E', // data-4
        0.8: '#B8863F', // warning
        1.0: '#C1352B'  // critical
      }
    }).addTo(map);
    
    return () => {
      map.removeLayer(layer);
    };
  }, [map, points]);

  return null;
}

// Component to handle anomaly pulsing markers
function AnomalyMarkers({ anomalies }: { anomalies: any[] }) {
  const map = useMap();
  
  useEffect(() => {
    const markers = anomalies.map(point => {
      const icon = L.divIcon({
        className: 'bg-transparent',
        html: `<div class="relative w-8 h-8 flex items-center justify-center">
                 <div class="absolute w-2 h-2 bg-[var(--accent-critical)] rounded-full z-10"></div>
                 <div class="absolute w-8 h-8 border-[1.5px] border-[var(--accent-critical)] rounded-full animate-hotspot-pulse"></div>
               </div>`,
        iconSize: [32, 32],
        iconAnchor: [16, 16]
      });
      return L.marker([point.lat, point.lng], { icon }).addTo(map);
    });
    
    return () => {
      markers.forEach(m => map.removeLayer(m));
    };
  }, [map, anomalies]);

  return null;
}

export function HotspotMap() {
  const { selectedDistrictId, setSelectedDistrictId, timeOfDayFilter, setTimeOfDayFilter } = useIntel();
  
  const { data: hotspotData } = useListHotspots({ districtId: selectedDistrictId || undefined, timeOfDay: timeOfDayFilter >= 0 ? timeOfDayFilter : undefined });
  const { data: districtData } = useListDistricts();
  
  const hotspots = Array.isArray(hotspotData) ? hotspotData : [];
  const districts = Array.isArray(districtData) ? districtData : [];

  // Format points for heatmap: [lat, lng, intensity]
  const heatPoints: Array<[number, number, number]> = hotspots.map(h => [h.lat, h.lng, h.intensity]);
  const anomalies = hotspots.filter(h => h.isAnomaly);
  const blindSpots = districts.filter(d => d.isBlindSpot);

  const [showBlindSpots, setShowBlindSpots] = useState(false);

  return (
    <PageTransition className="space-y-6 h-[calc(100vh-120px)] flex flex-col pb-4">
      <header className="flex justify-between items-end shrink-0">
        <div>
          <h1 className="text-section-header">Hotspot Map</h1>
          <p className="text-body text-[var(--ink-secondary)] mt-1">Geospatial anomaly detection and risk coverage.</p>
        </div>
        
        <div className="flex gap-4">
          <label className="flex items-center gap-2 text-[13px] font-medium cursor-pointer">
            <input 
              type="checkbox" 
              checked={showBlindSpots}
              onChange={(e) => setShowBlindSpots(e.target.checked)}
              className="rounded border-[var(--border-hairline)] text-[var(--accent-focus)] focus:ring-[var(--accent-focus)]"
            />
            Overlay Blind Spots
          </label>
        </div>
      </header>

      <div className="card-base p-0 flex-1 flex flex-col md:flex-row overflow-hidden relative border-[var(--border-hairline)]">
        {/* Sidebar Controls */}
        <div className="w-full md:w-64 bg-[var(--bg-canvas)] border-b md:border-b-0 md:border-r border-[var(--border-hairline)] p-4 flex flex-col gap-6 z-20 shadow-[2px_0_12px_rgba(0,0,0,0.02)]">
          <div>
            <div className="text-[10px] font-mono uppercase tracking-wider text-[var(--ink-tertiary)] mb-3">District Filter</div>
            <select 
              value={selectedDistrictId || ''}
              onChange={(e) => setSelectedDistrictId(e.target.value || null)}
              className="w-full bg-[var(--bg-surface)] border border-[var(--border-hairline)] rounded-[4px] p-2 text-[13px] focus:outline-none focus:ring-1 focus:ring-[var(--accent-focus)]"
            >
              <option value="">All Karnataka</option>
              {districts.map(d => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
            </select>
          </div>

          <div>
            <div className="text-[10px] font-mono uppercase tracking-wider text-[var(--ink-tertiary)] mb-3 flex justify-between">
              <span>Time Scrubber</span>
              <span>{timeOfDayFilter >= 0 ? `${timeOfDayFilter.toString().padStart(2, '0')}:00` : 'All'}</span>
            </div>
            <input 
              type="range" 
              min="-1" 
              max="23" 
              value={timeOfDayFilter}
              onChange={(e) => setTimeOfDayFilter(parseInt(e.target.value))}
              className="w-full accent-[var(--accent-focus)]"
            />
            <div className="flex justify-between text-[10px] text-[var(--ink-tertiary)] mt-1 font-mono">
              <span>All</span>
              <span>12</span>
              <span>23</span>
            </div>
          </div>

          <div className="mt-auto">
            <div className="text-[10px] font-mono uppercase tracking-wider text-[var(--ink-tertiary)] mb-2">Legend</div>
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[var(--accent-critical)]"></div>
                <span className="text-[12px] text-[var(--ink-secondary)]">Critical Anomaly</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[var(--accent-warning)] opacity-80"></div>
                <span className="text-[12px] text-[var(--ink-secondary)]">Flagged Risk</span>
              </div>
              <div className="w-full h-2 rounded-full mt-2 bg-gradient-to-r from-[var(--data-2)] via-[var(--data-4)] to-[var(--accent-critical)]"></div>
              <div className="flex justify-between text-[10px] font-mono text-[var(--ink-tertiary)]">
                <span>Low</span>
                <span>High</span>
              </div>
            </div>
          </div>
        </div>

        {/* Map Area */}
        <div className="flex-1 relative bg-[var(--bg-canvas)]">
          <MapContainer 
            center={[14.5, 76.5]} // Center of Karnataka roughly
            zoom={7} 
            style={{ height: '100%', width: '100%', background: 'var(--bg-canvas)' }}
            zoomControl={false}
          >
            <TileLayer
              attribution='&copy; <a href="https://carto.com/">CartoDB</a>'
              url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
            />
            
            <HeatLayer points={heatPoints} />
            <AnomalyMarkers anomalies={anomalies} />

            {/* Blind Spot Overlays */}
            {showBlindSpots && blindSpots.map(d => (
              <div key={`bs-${d.id}`}>
                {/* We use standard markers with custom HTML to simulate an overlay region for mock purposes */}
                {/* In a real app, this would be a GeoJSON layer with borders */}
              </div>
            ))}
          </MapContainer>

          {/* Floating UI for Blind Spots if toggled */}
          {showBlindSpots && blindSpots.map(bs => (
            <div key={bs.id} className="absolute top-4 right-4 max-w-[280px] card-base shadow-lg border-[var(--accent-warning)] p-3 z-[400] animate-in fade-in slide-in-from-right-4">
              <div className="flex items-start gap-2">
                <div className="w-2 h-2 rounded-full bg-[var(--accent-warning)] mt-1.5 shrink-0 animate-pulse"></div>
                <div>
                  <div className="text-[13px] font-medium text-[var(--ink-primary)]">Blind-Spot: {bs.name}</div>
                  <p className="text-[11px] text-[var(--ink-secondary)] mt-1 leading-relaxed">
                    {bs.blindSpotReason}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </PageTransition>
  );
}

