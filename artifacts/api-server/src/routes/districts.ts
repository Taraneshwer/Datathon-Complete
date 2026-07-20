import { Router, type IRouter } from "express";
import { districts, hotspots } from "../mockData";

const router: IRouter = Router();

router.get("/districts", (_req, res) => {
  res.json(districts);
});

router.get("/hotspots", (req, res): void => {
  const { districtId, timeOfDay, crimeType, blindSpot } = req.query;

  let result = [...hotspots];

  if (districtId && typeof districtId === "string") {
    result = result.filter((h) => h.districtId === districtId);
  }
  if (timeOfDay !== undefined) {
    const hour = parseInt(timeOfDay as string, 10);
    if (!isNaN(hour) && hour >= 0 && hour <= 23) {
      // return hotspots within ±3 hours of requested time
      result = result.filter((h) => Math.abs(h.timeOfDay - hour) <= 3);
    }
  }
  if (crimeType && typeof crimeType === "string") {
    result = result.filter(
      (h) => h.crimeType.toLowerCase() === crimeType.toLowerCase()
    );
  }
  if (blindSpot === "true") {
    // For blind-spot mode, return district-level indicators instead
    const blindSpotDistricts = districts.filter((d) => d.isBlindSpot);
    res.json(
      blindSpotDistricts.map((d) => ({
        id: `bs-${d.id}`,
        lat: d.lat,
        lng: d.lng,
        intensity: 0.6,
        districtId: d.id,
        crimeType: "BlindSpot",
        timeOfDay: -1,
        isAnomaly: false,
        stationName: null,
        isBlindSpot: true,
        blindSpotReason: d.blindSpotReason,
      }))
    );
    return;
  }

  res.json(result);
});

export default router;
