"""
app/intelligence/hotspot_predictor.py
─────────────────────────────────────────────────────────────────────────────
Geographic crime hotspot prediction using DBSCAN clustering.

Design:
  - DBSCAN runs inside asyncio.to_thread() to avoid blocking the event loop
    (scikit-learn is CPU-bound / GIL-holding).
  - Epsilon (eps) is specified in degrees of lat/lon; 0.5° ≈ 55 km.
  - Noise points (cluster_id == -1) are counted and returned separately.
  - Cluster centroids are computed as the mean of member coordinates.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, NamedTuple

from app.config import get_settings
from app.models.schemas import ClusterResult, CoordinatePoint, HotspotResponse

logger = logging.getLogger(__name__)


class _ClusterOutput(NamedTuple):
    labels: Any
    coords: Any


class HotspotPredictor:
    """
    Async geographic crime hotspot predictor using DBSCAN.

    Usage:
        predictor = HotspotPredictor()
        result = await predictor.predict(coordinates)
    """

    def __init__(self) -> None:
        self._settings = get_settings()

    async def predict(self, coordinates: list[CoordinatePoint]) -> HotspotResponse:
        """
        Cluster geographic coordinates and return hotspot summaries.

        Args:
            coordinates: List of lat/lon points (minimum 3 required).

        Returns:
            HotspotResponse with clusters, centroids, and noise count.

        Raises:
            ValueError: If fewer than 3 coordinates are provided.
        """
        if len(coordinates) < 3:
            raise ValueError(
                "At least 3 coordinate points are required for clustering."
            )

        settings = self._settings
        logger.debug(
            "HotspotPredictor: clustering %d points | eps=%.3f min_samples=%d",
            len(coordinates),
            settings.dbscan_eps,
            settings.dbscan_min_samples,
        )

        # Offload CPU-bound clustering to a thread pool
        output = await asyncio.to_thread(
            self._run_dbscan,
            coordinates,
            settings.dbscan_eps,
            settings.dbscan_min_samples,
        )

        clusters = self._build_cluster_results(output, coordinates)
        noise_count = int(np.sum(output.labels == -1))

        logger.info(
            "HotspotPredictor: found %d clusters, %d noise points",
            len(clusters),
            noise_count,
        )

        return HotspotResponse(
            total_points=len(coordinates),
            noise_points=noise_count,
            clusters=clusters,
        )

    @staticmethod
    def _run_dbscan(
        coordinates: list[CoordinatePoint],
        eps: float,
        min_samples: int,
    ) -> _ClusterOutput:
        """
        Synchronous DBSCAN execution (runs in thread pool).
        Uses haversine metric for geographically accurate distance.
        """
        try:
            import numpy as np
            from sklearn.cluster import DBSCAN
        except ImportError as exc:
            raise RuntimeError("scikit-learn and numpy must be installed to run DBSCAN clustering: " + str(exc)) from exc

        coords = np.array(
            [[p.latitude, p.longitude] for p in coordinates],
            dtype=np.float64,
        )

        # Convert degrees to radians for haversine metric
        coords_rad = np.radians(coords)

        # eps in haversine terms: eps_degrees / 180 * π / (earth_radius_km / 6371)
        # Simpler: pass eps in km, use metric="haversine" which expects radians
        # Here we use eps in degrees converted to radians (0.5° ≈ 0.00873 rad ≈ 55 km)
        eps_rad = np.radians(eps)

        db = DBSCAN(
            eps=eps_rad,
            min_samples=min_samples,
            algorithm="ball_tree",
            metric="haversine",
            n_jobs=-1,             # Use all CPU cores
        )
        labels: NDArray[np.intp] = db.fit_predict(coords_rad)
        return _ClusterOutput(labels=labels, coords=coords)

    @staticmethod
    def _build_cluster_results(
        output: _ClusterOutput,
        coordinates: list[CoordinatePoint],
    ) -> list[ClusterResult]:
        """
        Aggregate DBSCAN labels into cluster summary objects.
        """
        import numpy as np

        labels = output.labels
        coords = output.coords

        unique_ids = set(labels) - {-1}  # Exclude noise label
        results: list[ClusterResult] = []

        for cluster_id in sorted(unique_ids):
            mask: NDArray[np.bool_] = labels == cluster_id
            indices = [int(i) for i in np.where(mask)[0]]
            member_coords = coords[mask]

            centroid = member_coords.mean(axis=0)
            results.append(
                ClusterResult(
                    cluster_id=int(cluster_id),
                    centroid_latitude=round(float(centroid[0]), 6),
                    centroid_longitude=round(float(centroid[1]), 6),
                    point_count=int(mask.sum()),
                    point_indices=indices,
                )
            )

        return results

    async def predict_from_raw(
        self, lat_lon_pairs: list[tuple[float, float]]
    ) -> HotspotResponse:
        """
        Convenience method accepting raw (lat, lon) tuples.
        """
        coordinates = [
            CoordinatePoint(latitude=lat, longitude=lon)
            for lat, lon in lat_lon_pairs
        ]
        return await self.predict(coordinates)
