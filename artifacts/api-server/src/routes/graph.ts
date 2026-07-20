import { Router, type IRouter } from "express";
import { graphNodes, graphEdges, cases } from "../mockData";

const router: IRouter = Router();

router.get("/graph/nodes", (req, res) => {
  const { caseId, districtId, patternId, timeIndex } = req.query;

  let result = [...graphNodes];

  if (caseId && typeof caseId === "string") {
    result = result.filter((n) => n.linkedCaseIds.includes(caseId));
  }
  if (districtId && typeof districtId === "string") {
    // Filter to suspects/cases linked to this district
    const districtCases = cases
      .filter((c) => c.districtId === districtId)
      .map((c) => c.id);
    result = result.filter(
      (n) =>
        n.linkedCaseIds.some((id: string) => districtCases.includes(id)) ||
        n.type === "location"
    );
  }
  if (patternId && typeof patternId === "string") {
    const { patterns } = require("../mockData");
    const pattern = patterns.find((p: any) => p.id === patternId);
    if (pattern) {
      result = result.filter((n) =>
        n.linkedCaseIds.some((id: string) => pattern.matchedCaseIds.includes(id))
      );
    }
  }
  if (timeIndex !== undefined) {
    const ti = parseInt(timeIndex as string, 10);
    if (!isNaN(ti)) {
      result = result.filter((n) => n.timeIndex <= ti);
    }
  }

  res.json(result);
});

router.get("/graph/edges", (req, res) => {
  const { caseId, districtId, patternId, timeIndex } = req.query;

  let result = [...graphEdges];

  if (timeIndex !== undefined) {
    const ti = parseInt(timeIndex as string, 10);
    if (!isNaN(ti)) {
      result = result.filter((e) => e.timeIndex <= ti);
    }
  }

  res.json(result);
});

export default router;
