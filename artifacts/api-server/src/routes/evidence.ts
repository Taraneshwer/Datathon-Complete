import { Router, type IRouter } from "express";
import { evidence, timelines, cases } from "../mockData";

const router: IRouter = Router();

router.get("/cases/:id/evidence", (req, res): void => {
  const { id } = req.params;
  const c = cases.find((c) => c.id === id);
  if (!c) { res.status(404).json({ error: "Case not found" }); return; }

  const items = evidence[id] ?? [];
  res.json(items);
});

router.get("/cases/:id/timeline", (req, res): void => {
  const { id } = req.params;
  const c = cases.find((c) => c.id === id);
  if (!c) { res.status(404).json({ error: "Case not found" }); return; }

  const events = (timelines[id] ?? []).sort(
    (a: any, b: any) =>
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );
  res.json(events);
});

export default router;
