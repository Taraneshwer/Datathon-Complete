import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet.heat";
import { Globe, Layers, Navigation } from "lucide-react";

declare module "leaflet" {
  function heatLayer(latlngs: Array<[number, number, number]>, options?: any): any;
}

export type MapPoint = {
  lat: number;
  lng: number;
  weight?: number;
  label?: string;
  tone?: "critical" | "warning" | "info" | "success";
};

type Props = {
  center?: { lat: number; lng: number };
  zoom?: number;
  heatmap?: MapPoint[];
  markers?: MapPoint[];
  variant?: "roadmap" | "satellite" | "hybrid";
  showControls?: boolean;
  className?: string;
  height?: number | string;
};

// Bengaluru default coordinates
const DEFAULT_CENTER = { lat: 12.9716, lng: 77.5946 };

export function OpenStreetMap({
  center = DEFAULT_CENTER,
  zoom = 11,
  heatmap,
  markers,
  showControls = true,
  className = "",
  height = 460,
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const heatLayerRef = useRef<any>(null);
  const markersRef = useRef<L.LayerGroup | null>(null);

  // Initialize map instance
  useEffect(() => {
    if (!containerRef.current) return;

    if (!mapRef.current) {
      const map = L.map(containerRef.current, {
        center: [center.lat, center.lng],
        zoom,
        zoomControl: showControls,
      });

      // Standard OpenStreetMap Tile Layer
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(map);

      markersRef.current = L.layerGroup().addTo(map);
      mapRef.current = map;
    }

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  // Update center and zoom when props change
  useEffect(() => {
    if (mapRef.current) {
      mapRef.current.setView([center.lat, center.lng], zoom);
    }
  }, [center.lat, center.lng, zoom]);

  // Update heatmap layer
  useEffect(() => {
    if (!mapRef.current) return;

    if (heatLayerRef.current) {
      mapRef.current.removeLayer(heatLayerRef.current);
      heatLayerRef.current = null;
    }

    if (heatmap && heatmap.length > 0) {
      const points: Array<[number, number, number]> = heatmap.map((p) => [
        p.lat,
        p.lng,
        p.weight ?? 1,
      ]);

      heatLayerRef.current = L.heatLayer(points, {
        radius: 25,
        blur: 15,
        maxZoom: 13,
        gradient: {
          0.2: "rgba(11,31,58,0.4)",
          0.4: "rgba(166,139,91,0.6)",
          0.6: "rgba(201,162,39,0.8)",
          0.8: "rgba(220,80,50,0.9)",
          1.0: "rgba(193,53,43,1)",
        },
      }).addTo(mapRef.current);
    }
  }, [heatmap]);

  // Update markers
  useEffect(() => {
    if (!mapRef.current || !markersRef.current) return;

    markersRef.current.clearLayers();

    if (markers && markers.length > 0) {
      markers.forEach((m) => {
        const color = toneColor(m.tone);
        const customIcon = L.divIcon({
          className: "osm-custom-marker",
          html: `<div style="
            width: 14px;
            height: 14px;
            background-color: ${color};
            border: 2px solid white;
            border-radius: 50%;
            box-shadow: 0 0 8px ${color}80;
          "></div>`,
          iconSize: [14, 14],
          iconAnchor: [7, 7],
        });

        const marker = L.marker([m.lat, m.lng], { icon: customIcon });
        if (m.label) {
          marker.bindTooltip(m.label, {
            permanent: false,
            direction: "top",
            className: "osm-marker-tooltip",
          });
        }
        markersRef.current?.addLayer(marker);
      });
    }
  }, [markers]);

  return (
    <div className={`relative govt-card overflow-hidden ${className}`} style={{ height }}>
      <div ref={containerRef} className="absolute inset-0 z-0" />
      <div className="absolute top-3 left-3 z-[400] flex items-center gap-1.5 rounded-md bg-navy-deep/90 text-white text-[11px] px-2.5 py-1.5 backdrop-blur shadow-md">
        <Globe className="h-3.5 w-3.5 text-gold" />
        <span className="font-semibold tracking-wide">OPENSTREETMAP • LIVE</span>
      </div>
      <div className="absolute bottom-3 right-3 z-[400] flex items-center gap-2 text-[10px] text-slate-700 bg-white/80 px-2 py-1 rounded backdrop-blur border border-slate-200">
        <Layers className="h-3 w-3" /> OSM Layer
        <Navigation className="h-3 w-3 ml-2" /> Karnataka
      </div>
    </div>
  );
}

// Legacy alias for compatibility
export const GoogleMap = OpenStreetMap;

function toneColor(t?: MapPoint["tone"]) {
  switch (t) {
    case "critical": return "#C1352B";
    case "warning":  return "#C9A227";
    case "success":  return "#2F855A";
    default:         return "#1E40AF";
  }
}
