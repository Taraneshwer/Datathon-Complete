import { Router, type IRouter } from "express";
import { accessLog, ledgerStatus } from "../mockData";

const router: IRouter = Router();

// Simulate incrementing block height every ~30s
let blockHeight = ledgerStatus.blockHeight;
setInterval(() => {
  blockHeight++;
}, 30000);

router.get("/trust/access-log", (req, res) => {
  const { limit } = req.query;

  let result = [...accessLog].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  if (limit) {
    const n = parseInt(limit as string, 10);
    if (!isNaN(n)) result = result.slice(0, n);
  }

  res.json(result);
});

router.get("/trust/ledger-status", (_req, res) => {
  res.json({
    ...ledgerStatus,
    blockHeight,
  });
});

export default router;
