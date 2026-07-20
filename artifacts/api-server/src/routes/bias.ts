import { Router, type IRouter } from "express";
import { biasAuditData } from "../mockData";

const router: IRouter = Router();

router.get("/bias/audit", (_req, res) => {
  res.json(biasAuditData);
});

export default router;
