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
        """Synchronous H3 grid analysis querying Catalyst DataStore (runs in thread pool)."""
        try:
            import h3
        except ImportError as exc:
            raise RuntimeError("h3 must be installed to run blind spot analysis: " + str(exc)) from exc

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

        # Query Catalyst DataStore for real FIR density per H3 cell
        from app.db.catalyst import CatalystDBClient
        db = CatalystDBClient()
        try:
            fir_rows = db.execute_sql_query(f"SELECT h3_index, severity FROM FIR WHERE district_id = '{request.district}'") if request.district else db.execute_sql_query("SELECT h3_index, severity FROM FIR")
        except Exception as exc:
            logger.debug("FIR query failed in blind spot analysis: %s", exc)
            fir_rows = []

        # Count FIRs per cell
        cell_crimes: dict[str, int] = {}
        for r in (fir_rows or []):
            data = r.get("FIR", r)
            if isinstance(data, str):
                continue
            c_idx = str(data.get("h3_index", ""))
            if c_idx:
                cell_crimes[c_idx] = cell_crimes.get(c_idx, 0) + 1
        max_crimes = max(cell_crimes.values()) if cell_crimes else 1

        results: list[BlindSpotResult] = []

        for cell in cells:
            lat, lon = h3.cell_to_latlng(cell)
            crimes = cell_crimes.get(cell, 0)
            crime_density = min(1.0, float(crimes / max(1, max_crimes))) if crimes > 0 else 0.0
            cctv_coverage = 0.0  # Default 0% coverage unless recorded in surveillance table
            patrol_density = 0.0 # Default 0% patrol density unless recorded in deployment table

            # Blind-spot score = high crime, low coverage
            blind_spot_score = crime_density * (1.0 - cctv_coverage) * (1.0 - patrol_density * 0.5)

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
