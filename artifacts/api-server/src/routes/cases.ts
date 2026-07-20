import { Router, type IRouter } from "express";
import { cases, suspects, victims } from "../mockData";

const router: IRouter = Router();

router.get("/cases", (req, res) => {
  const { status, districtId, suspectId, patternId, limit } = req.query;

  let result = [...cases];

  if (status && typeof status === "string") {
    result = result.filter((c) => c.status === status);
  }
  if (districtId && typeof districtId === "string") {
    result = result.filter((c) => c.districtId === districtId);
  }
  if (suspectId && typeof suspectId === "string") {
    result = result.filter((c) => c.suspectIds.includes(suspectId));
  }
  if (patternId && typeof patternId === "string") {
    result = result.filter((c) => c.patternId === patternId);
  }
  if (limit) {
    const n = parseInt(limit as string, 10);
    if (!isNaN(n)) result = result.slice(0, n);
  }

  res.json(result);
});

router.get("/cases/summary", (_req, res) => {
  const total = cases.length;
  const open = cases.filter((c) => c.status === "open").length;
  const underReview = cases.filter((c) => c.status === "under_review").length;
  const closed = cases.filter((c) => c.status === "closed").length;

  const districtMap: Record<string, { districtId: string; districtName: string; count: number }> = {};
  for (const c of cases) {
    if (!districtMap[c.districtId]) {
      districtMap[c.districtId] = { districtId: c.districtId, districtName: c.districtName, count: 0 };
    }
    districtMap[c.districtId].count++;
  }

  res.json({
    total,
    open,
    underReview,
    closed,
    byDistrict: Object.values(districtMap),
  });
});

router.get("/cases/:id", (req, res): void => {
  const { id } = req.params;
  const c = cases.find((c) => c.id === id);
  if (!c) { res.status(404).json({ error: "Case not found" }); return; }

  const linkedCaseIds = cases
    .filter((other) =>
      other.id !== id &&
      (other.suspectIds.some((s) => c.suspectIds.includes(s)) || other.patternId === c.patternId)
    )
    .map((other) => other.id)
    .slice(0, 4);

  res.json({
    ...c,
    summary: `Case ${c.id} — ${c.crimeType} incident in ${c.districtName}. ${c.confidence * 100}% pattern-match confidence. Officer in charge: ${c.officerInCharge}.`,
    evidenceCount: 3,
    linkedCaseIds,
  });
});

export default router;
