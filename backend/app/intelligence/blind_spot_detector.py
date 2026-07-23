"""
app/intelligence/blind_spot_detector.py
─────────────────────────────────────────────────────────────────────────────
Crime Blind-Spot Discovery Engine.

Analyzes a geographic district using H3 hexagonal grid cells to identify
areas with high crime density but insufficient surveillance coverage.

Inputs: crime coordinate density, a simulated CCTV coverage map
Outputs: H3-indexed blind spots with recommendations for resource deployment
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import asyncio
import logging

import h3
import numpy as np

from app.config import get_settings
from app.models.schemas import (
    BlindSpotRequest,
    BlindSpotResponse,
    BlindSpotResult,
)

logger = logging.getLogger(__name__)

# Resource deployment recommendations by blind-spot score
_RECOMMENDATIONS_MAP: dict[str, list[str]] = {
    "critical": [
        "Install CCTV cameras immediately",
        "Deploy permanent patrol post",
        "Install emergency response booth",
        "Add street lighting",
        "Establish community policing unit",
    ],
    "high": [
        "Install CCTV cameras",
        "Increase patrol frequency",
        "Install emergency call points",
        "Improve street lighting",
    ],
    "medium": [
        "Schedule regular patrol passes",
        "Conduct community awareness program",
        "Evaluate CCTV placement",
    ],
    "low": [
        "Monitor for trend changes",
    ],
}


class BlindSpotDetector:
    """
    Identifies surveillance blind spots using H3 hexagonal grid analysis.
    CPU-bound computation runs in asyncio.to_thread().
    """

    def __init__(self) -> None:
        self._settings = get_settings()

    async def detect(self, request: BlindSpotRequest) -> BlindSpotResponse:
        """
        Identify blind spots in a geographic bounding box.
        Uses H3 cells at the configured resolution.
        """
        resolution = self._settings.h3_resolution

        logger.info(
            "BlindSpotDetector: analyzing district='%s' resolution=%d",
            request.district, resolution,
        )

        results = await asyncio.to_thread(
            self._run_analysis,
            request,
            resolution,
        )

        blind_spots = [r for r in results if r.blind_spot_score >= 0.5]

        logger.info(
            "BlindSpotDetector: %d/%d cells are blind spots",
            len(blind_spots), len(results),
        )

        return BlindSpotResponse(
            district=request.district,
            total_cells_analyzed=len(results),
            blind_spots_found=len(blind_spots),
            results=blind_spots,
        )

    @staticmethod
    def _run_analysis(
        request: BlindSpotRequest, resolution: int
    ) -> list[BlindSpotResult]:
        """Synchronous H3 grid analysis (runs in thread pool)."""
        # Generate H3 cells covering the bounding box
        cells = h3.geo_to_cells(
            {
                "type": "Polygon",
                "coordinates": [[
                    [request.longitude_min, request.latitude_min],
                    [request.longitude_max, request.latitude_min],
                    [request.longitude_max, request.latitude_max],
                    [request.longitude_min, request.latitude_max],
                    [request.longitude_min, request.latitude_min],
                ]],
            },
            resolution,
        )

        results: list[BlindSpotResult] = []
        rng = np.random.default_rng(42)  # Deterministic for reproducibility

        for cell in cells:
            lat, lon = h3.cell_to_latlng(cell)

            # In production: query actual crime DB and CCTV registry
            # Here we compute a plausible simulated score for demonstration
            crime_density = float(rng.beta(2, 5))       # 0–1, skewed toward low
            cctv_coverage = float(rng.beta(3, 4))        # 0–1
            patrol_density = float(rng.beta(3, 4))       # 0–1

            # Blind-spot score = high crime, low coverage
            blind_spot_score = crime_density * (1 - cctv_coverage) * (1 - patrol_density * 0.5)

            level = (
                "critical" if blind_spot_score > 0.7
                else "high" if blind_spot_score > 0.5
                else "medium" if blind_spot_score > 0.3
                else "low"
            )

            recs = _RECOMMENDATIONS_MAP.get(level, [])

            results.append(BlindSpotResult(
                h3_index=cell,
                centroid_latitude=round(lat, 6),
                centroid_longitude=round(lon, 6),
                crime_density=round(crime_density, 3),
                cctv_coverage=round(cctv_coverage, 3),
                patrol_density=round(patrol_density, 3),
                blind_spot_score=round(blind_spot_score, 3),
                recommendations=recs,
            ))

        # Sort by blind-spot score descending
        results.sort(key=lambda r: r.blind_spot_score, reverse=True)
        return results
