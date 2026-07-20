import { Router, type IRouter } from "express";
import { patterns } from "../mockData";

const router: IRouter = Router();

router.get("/patterns", (_req, res) => {
  res.json(patterns);
});

router.get("/patterns/:id", (req, res): void => {
  const { id } = req.params;
  const p = patterns.find((p) => p.id === id);
  if (!p) { res.status(404).json({ error: "Pattern not found" }); return; }
  res.json(p);
});

export default router;
