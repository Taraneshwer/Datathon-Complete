import { Router, type IRouter } from "express";
import healthRouter from "./health";
import districtsRouter from "./districts";
import casesRouter from "./cases";
import suspectsRouter from "./suspects";
import graphRouter from "./graph";
import patternsRouter from "./patterns";
import analyticsRouter from "./analytics";
import alertsRouter from "./alerts";
import evidenceRouter from "./evidence";
import biasRouter from "./bias";
import trustRouter from "./trust";

const router: IRouter = Router();

router.use(healthRouter);
router.use(districtsRouter);
router.use(casesRouter);
router.use(suspectsRouter);
router.use(graphRouter);
router.use(patternsRouter);
router.use(analyticsRouter);
router.use(alertsRouter);
router.use(evidenceRouter);
router.use(biasRouter);
router.use(trustRouter);

export default router;
