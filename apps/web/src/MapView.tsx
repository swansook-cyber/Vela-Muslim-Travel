import { useEffect, useRef } from "react";
import {
  GeoJSONSource,
  LngLatBounds,
  Map,
  Marker,
  NavigationControl,
  Popup,
  type StyleSpecification,
} from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

import type { AlongRouteResponse, PlaceResult } from "./types";

interface MapViewProps {
  route: AlongRouteResponse["route"] | null;
  places: PlaceResult[];
}

const style: StyleSpecification = {
  version: 8,
  sources: {
    osm: {
      type: "raster",
      tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
      tileSize: 256,
      attribution: "© OpenStreetMap contributors",
    },
  },
  layers: [
    {
      id: "osm",
      type: "raster",
      source: "osm",
    },
  ],
};

export function MapView({ route, places }: MapViewProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<Map | null>(null);
  const markersRef = useRef<Marker[]>([]);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) {
      return;
    }

    const map = new Map({
      container: containerRef.current,
      style,
      center: [100.5, 13.0],
      zoom: 5,
    });

    mapRef.current = map;
    map.addControl(new NavigationControl(), "top-right");

    return () => {
      markersRef.current.forEach((marker) => marker.remove());
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) {
      return;
    }

    const update = () => {
      if (route) {
        const data: GeoJSON.Feature<GeoJSON.LineString> = {
          type: "Feature",
          properties: {},
          geometry: route.geometry,
        };

        const existing = map.getSource("route") as GeoJSONSource | undefined;
        if (existing) {
          existing.setData(data);
        } else {
          map.addSource("route", {
            type: "geojson",
            data,
          });
          map.addLayer({
            id: "route-line",
            type: "line",
            source: "route",
            paint: {
              "line-width": 5,
            },
          });
        }
      } else if (map.getLayer("route-line")) {
        map.removeLayer("route-line");
        map.removeSource("route");
      }

      markersRef.current.forEach((marker) => marker.remove());
      markersRef.current = places.map((place) =>
        new Marker()
          .setLngLat([place.longitude, place.latitude])
          .setPopup(
            new Popup({ offset: 20 }).setText(
              `${place.name_th} · ${place.place_type}`,
            ),
          )
          .addTo(map),
      );

      const bounds = new LngLatBounds();
      if (route) {
        route.geometry.coordinates.forEach(([longitude, latitude]) => {
          bounds.extend([longitude, latitude]);
        });
      } else {
        places.forEach((place) => {
          bounds.extend([place.longitude, place.latitude]);
        });
      }

      if (!bounds.isEmpty()) {
        map.fitBounds(bounds, {
          padding: 48,
          maxZoom: route ? 11 : 13,
        });
      }
    };

    if (map.loaded()) {
      update();
    } else {
      map.once("load", update);
    }
  }, [route, places]);

  return <div ref={containerRef} className="map" aria-label="แผนที่เส้นทาง" />;
}
