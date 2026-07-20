import { Router, type IRouter } from "express";
import { alerts, riskForecast } from "../mockData";

const router: IRouter = Router();

router.get("/alerts", (req, res) => {
  const { read, severity } = req.query;

  let result = [...alerts].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  if (read !== undefined) {
    const isRead = read === "true";
    result = result.filter((a) => a.read === isRead);
  }
  if (severity && typeof severity === "string") {
    result = result.filter((a) => a.severity === severity);
  }

  res.json(result);
});

router.get("/alerts/risk-forecast", (_req, res) => {
  res.json(riskForecast);
});

export default router;
