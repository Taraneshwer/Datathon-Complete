import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bot, Mic, Send, Sparkles, X, ShieldAlert } from "lucide-react";

const SUGGESTIONS = [
  "Summarize Case #KA-2891 in 3 lines",
  "Show suspects linked to vehicle KA-05-MH-1234",
  "Predict next hotspot in South Bengaluru",
  "Draft FIR narrative from evidence log",
];

export function FloatingAI() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 16, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 16, scale: 0.96 }}
            transition={{ type: "spring", damping: 22, stiffness: 260 }}
            className="fixed bottom-24 right-6 z-50 w-[380px] max-w-[calc(100vw-2rem)] govt-card topline overflow-hidden shadow-2xl"
          >
            <header className="flex items-center justify-between px-4 py-3 bg-navy-deep text-white">
              <div className="flex items-center gap-2">
                <div className="h-7 w-7 rounded-md grid place-items-center bg-gold/20 text-gold">
                  <Sparkles className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-xs font-semibold tracking-wider">DRISHTI · INVESTIGATIVE AI</p>
                  <p className="text-[10px] text-white/60 flex items-center gap-1">
                    <ShieldAlert className="h-3 w-3 text-success" /> Prompt firewall active
                  </p>
                </div>
              </div>
              <button onClick={() => setOpen(false)} className="text-white/70 hover:text-white">
                <X className="h-4 w-4" />
              </button>
            </header>

            <div className="p-4 space-y-3 max-h-[380px] overflow-y-auto">
              <div className="rounded-md bg-muted p-3 text-sm text-navy-deep">
                Good evening, Officer Rao. I've reviewed 4 open cases assigned to your desk. 2 have new evidence, 1 was flagged by the bias detector.
              </div>
              <p className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Suggestions</p>
              <div className="grid gap-1.5">
                {SUGGESTIONS.map((s) => (
                  <button key={s} className="text-left text-[13px] px-3 py-2 rounded-md border border-border hover:border-gold hover:bg-accent transition-colors">
                    {s}
                  </button>
                ))}
              </div>
            </div>

            <div className="p-3 border-t border-border bg-muted/40">
              <div className="flex items-center gap-2 rounded-md bg-card border border-border px-3 py-2">
                <button className="text-muted-foreground hover:text-navy-deep"><Mic className="h-4 w-4" /></button>
                <input
                  placeholder="Ask an intel question…"
                  className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
                />
                <button className="h-7 w-7 rounded-md bg-navy-deep text-white grid place-items-center hover:bg-navy">
                  <Send className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setOpen((o) => !o)}
        className="fixed bottom-6 right-6 z-50 h-14 w-14 rounded-full bg-navy-deep text-white grid place-items-center shadow-xl ring-2 ring-gold/60"
        aria-label="Open Investigative AI"
      >
        <Bot className="h-6 w-6" />
        <span className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-success ring-2 ring-white animate-pulse" />
      </motion.button>
    </>
  );
}
