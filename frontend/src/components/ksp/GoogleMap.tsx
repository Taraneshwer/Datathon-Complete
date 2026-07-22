import { useEffect, useRef, useState } from "react";
import { AlertCircle, Layers, Satellite, Map as MapIcon, Navigation } from "lucide-react";

declare global {
  interface Window {
    google?: any;
    __kspMapCbs?: Array<() => void>;
    kspInitMaps?: () => void;
  }
}

const KEY = import.meta.env.VITE_LOVABLE_CONNECTOR_GOOGLE_MAPS_BROWSER_KEY as string | undefined;
const CHANNEL = import.meta.env.VITE_LOVABLE_CONNECTOR_GOOGLE_MAPS_TRACKING_ID as string | undefined;

let loading: Promise<void> | null = null;
function loadGoogleMaps(): Promise<void> {
  if (typeof window === "undefined") return Promise.reject();
  if (window.google?.maps) return Promise.resolve();
  if (loading) return loading;
  if (!KEY) return Promise.reject(new Error("no-key"));
  loading = new Promise((resolve, reject) => {
    window.__kspMapCbs = window.__kspMapCbs || [];
    window.kspInitMaps = () => window.__kspMapCbs?.forEach((cb) => cb());
    window.__kspMapCbs.push(() => resolve());
    const s = document.createElement("script");
    const params = new URLSearchParams({
      key: KEY,
      libraries: "visualization,places,drawing,geometry",
      loading: "async",
      callback: "kspInitMaps",
      ...(CHANNEL ? { channel: CHANNEL } : {}),
    });
    s.src = `https://maps.googleapis.com/maps/api/js?${params.toString()}`;
    s.async = true;
    s.onerror = () => reject(new Error("load-fail"));
    document.head.appendChild(s);
  });
  return loading;
}

export type MapPoint = { lat: number; lng: number; weight?: number; label?: string; tone?: "critical" | "warning" | "info" | "success" };

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

// Bengaluru default
const DEFAULT = { lat: 12.9716, lng: 77.5946 };

export function GoogleMap({
  center = DEFAULT, zoom = 11, heatmap, markers, variant = "roadmap",
  showControls = true, className = "", height = 460,
}: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const [state, setState] = useState<"loading" | "ready" | "fallback">("loading");
  const mapRef = useRef<any>(null);

  useEffect(() => {
    let cancelled = false;
    loadGoogleMaps()
      .then(() => {
        if (cancelled || !ref.current) return;
        const g = window.google;
        const map = new g.maps.Map(ref.current, {
          center, zoom, mapTypeId: variant,
          disableDefaultUI: !showControls,
          styles: mapStyle,
          streetViewControl: showControls,
          fullscreenControl: false,
        });
        mapRef.current = map;

        if (heatmap?.length && g.maps.visualization) {
          new g.maps.visualization.HeatmapLayer({
            data: heatmap.map((p) => ({
              location: new g.maps.LatLng(p.lat, p.lng),
              weight: p.weight ?? 1,
            })),
            radius: 32,
            opacity: 0.75,
            map,
            gradient: [
              "rgba(11,31,58,0)",
              "rgba(11,31,58,0.5)",
              "rgba(166,139,91,0.7)",
              "rgba(201,162,39,0.85)",
              "rgba(220,80,50,0.95)",
            ],
          });
        }

        markers?.forEach((m) => {
          new g.maps.Marker({
            position: { lat: m.lat, lng: m.lng },
            map,
            title: m.label,
            icon: {
              path: g.maps.SymbolPath.CIRCLE,
              scale: 7,
              fillColor: toneColor(m.tone),
              fillOpacity: 1,
              strokeColor: "#fff",
              strokeWeight: 2,
            },
          });
        });

        setState("ready");
      })
      .catch(() => !cancelled && setState("fallback"));
    return () => { cancelled = true; };
  }, [center.lat, center.lng, zoom, variant, showControls, heatmap, markers]);

  return (
    <div className={`relative govt-card overflow-hidden ${className}`} style={{ height }}>
      <div ref={ref} className="absolute inset-0" />
      {state !== "ready" && <MapFallback heatmap={heatmap} markers={markers} error={state === "fallback"} />}
      {state === "ready" && (
        <div className="absolute top-3 left-3 flex items-center gap-1.5 rounded-md bg-navy-deep/90 text-white text-[11px] px-2.5 py-1.5 backdrop-blur">
          <Satellite className="h-3.5 w-3.5 text-gold" />
          <span className="font-semibold tracking-wide">GOOGLE MAPS • LIVE</span>
        </div>
      )}
    </div>
  );
}

function toneColor(t?: MapPoint["tone"]) {
  switch (t) {
    case "critical": return "#c0392b";
    case "warning":  return "#c9a227";
    case "success":  return "#2f855a";
    default:         return "#1e40af";
  }
}

function MapFallback({ heatmap, markers, error }: { heatmap?: MapPoint[]; markers?: MapPoint[]; error?: boolean }) {
  // Stylized tactical grid with SVG heatmap points (Bengaluru bounds approximation)
  const pts = [...(heatmap ?? []), ...(markers ?? [])];
  const lats = pts.map(p => p.lat), lngs = pts.map(p => p.lng);
  const minLat = Math.min(...lats, 12.85), maxLat = Math.max(...lats, 13.10);
  const minLng = Math.min(...lngs, 77.45), maxLng = Math.max(...lngs, 77.75);
  const project = (p: { lat: number; lng: number }) => ({
    x: ((p.lng - minLng) / (maxLng - minLng)) * 100,
    y: (1 - (p.lat - minLat) / (maxLat - minLat)) * 100,
  });

  return (
    <div className="absolute inset-0 bg-[color:var(--navy-deep)] scanline overflow-hidden">
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
        <defs>
          <radialGradient id="heat">
            <stop offset="0%" stopColor="#dc5032" stopOpacity="0.75" />
            <stop offset="60%" stopColor="#c9a227" stopOpacity="0.35" />
            <stop offset="100%" stopColor="#0B1F3A" stopOpacity="0" />
          </radialGradient>
        </defs>
        {/* faux roads */}
        {[20, 45, 70].map((y) => (
          <line key={"h"+y} x1="0" y1={y} x2="100" y2={y + 3} stroke="rgba(255,255,255,0.06)" strokeWidth="0.4" />
        ))}
        {[25, 55, 80].map((x) => (
          <line key={"v"+x} x1={x} y1="0" x2={x + 4} y2="100" stroke="rgba(255,255,255,0.06)" strokeWidth="0.4" />
        ))}
        {heatmap?.map((p, i) => {
          const { x, y } = project(p);
          return <circle key={i} cx={x} cy={y} r={(p.weight ?? 1) * 5 + 3} fill="url(#heat)" />;
        })}
        {markers?.map((p, i) => {
          const { x, y } = project(p);
          return <circle key={i} cx={x} cy={y} r="1.2" fill={toneColor(p.tone)} stroke="#fff" strokeWidth="0.3" />;
        })}
      </svg>
      <div className="absolute top-3 left-3 flex items-center gap-1.5 rounded-md bg-black/40 text-white text-[11px] px-2.5 py-1.5">
        <MapIcon className="h-3.5 w-3.5 text-gold" />
        <span className="font-semibold tracking-wide">
          {error ? "TACTICAL VIEW • Configure Google Maps API" : "LOADING GOOGLE MAPS…"}
        </span>
      </div>
      {error && (
        <div className="absolute bottom-3 left-3 right-3 flex items-start gap-2 rounded-md bg-black/50 text-white/90 text-[11px] px-3 py-2 max-w-md">
          <AlertCircle className="h-3.5 w-3.5 shrink-0 text-gold mt-0.5" />
          <span>Connect the Google Maps Platform integration to enable live map, heatmap layer, marker clustering, directions and street view.</span>
        </div>
      )}
      <div className="absolute bottom-3 right-3 flex items-center gap-2 text-[10px] text-white/60">
        <Layers className="h-3 w-3" /> Overlay: Crime density
        <Navigation className="h-3 w-3 ml-2" /> KA / Bengaluru
      </div>
    </div>
  );
}

// Muted government-style map styling
const mapStyle = [
  { elementType: "geometry", stylers: [{ color: "#f5f5f2" }] },
  { elementType: "labels.text.fill", stylers: [{ color: "#5f6b7a" }] },
  { elementType: "labels.text.stroke", stylers: [{ color: "#ffffff" }] },
  { featureType: "administrative", elementType: "geometry.stroke", stylers: [{ color: "#c9a227" }] },
  { featureType: "poi", stylers: [{ visibility: "off" }] },
  { featureType: "road", elementType: "geometry", stylers: [{ color: "#ffffff" }] },
  { featureType: "road.arterial", elementType: "geometry", stylers: [{ color: "#e6e6df" }] },
  { featureType: "road.highway", elementType: "geometry", stylers: [{ color: "#d9c99a" }] },
  { featureType: "water", elementType: "geometry", stylers: [{ color: "#bcd4e6" }] },
  { featureType: "landscape", elementType: "geometry", stylers: [{ color: "#f5f5f2" }] },
];
