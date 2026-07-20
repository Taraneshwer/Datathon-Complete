import { Router, type IRouter } from "express";
import { trendData, dashboardAnalytics } from "../mockData";

const router: IRouter = Router();

router.get("/analytics/dashboard", (_req, res) => {
  res.json(dashboardAnalytics);
});

router.get("/analytics/trend", (req, res) => {
  const { districtId, months } = req.query;

  let result = [...trendData];

  if (months) {
    const n = parseInt(months as string, 10);
    if (!isNaN(n)) result = result.slice(-n);
  }

  // All trend data is currently for "all" districtId — for now return same data
  res.json(result);
});

export default router;
