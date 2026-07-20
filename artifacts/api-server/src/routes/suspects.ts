import { Router, type IRouter } from "express";
import { suspects, victims } from "../mockData";

const router: IRouter = Router();

router.get("/suspects", (req, res) => {
  const { caseId, districtId } = req.query;

  let result = [...suspects];

  if (caseId && typeof caseId === "string") {
    result = result.filter((s) => s.caseIds.includes(caseId));
  }
  if (districtId && typeof districtId === "string") {
    result = result.filter((s) => s.districtId === districtId);
  }

  res.json(result);
});

router.get("/suspects/:id", (req, res): void => {
  const { id } = req.params;
  const s = suspects.find((s) => s.id === id);
  if (!s) { res.status(404).json({ error: "Suspect not found" }); return; }
  res.json(s);
});

router.get("/victims", (req, res) => {
  const { caseId } = req.query;

  let result = [...victims];

  if (caseId && typeof caseId === "string") {
    result = result.filter((v) => v.caseIds.includes(caseId));
  }

  res.json(result);
});

export default router;
