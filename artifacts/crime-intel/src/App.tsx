import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Route, Switch, Router as WouterRouter, Redirect } from 'wouter';
import { IntelProvider } from './context/IntelContext';
import { ThemeProvider } from './context/ThemeContext';
import { Shell } from './components/Shell';

// Pages from YASH_REPLIT / YASH_LOVABLE
import { Dashboard } from './pages/Dashboard';
import { HotspotMap } from './pages/HotspotMap';
import { KnowledgeGraph } from './pages/KnowledgeGraph';
import { Patterns } from './pages/Patterns';
import { EarlyWarning } from './pages/EarlyWarning';
import { CaseEvidence } from './pages/CaseEvidence';
import { BiasAudit } from './pages/BiasAudit';
import { Agent } from './pages/Agent';
import { TrustOversight as Trust } from './pages/Trust';

// New Pages from PARIKSHITH_FORK
import { AiAssistant } from './pages/AiAssistant';
import { Analytics } from './pages/Analytics';
import { Blockchain } from './pages/Blockchain';
import { EvidenceHub } from './pages/EvidenceHub';
import { Identity } from './pages/Identity';
import { Investigations } from './pages/Investigations';
import { KnowledgeGraphKsp } from './pages/KnowledgeGraphKsp';
import { NationalAlerts } from './pages/NationalAlerts';
import { Prevention } from './pages/Prevention';
import { Replay } from './pages/Replay';
import { Settings } from './pages/Settings';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: false,
    },
  },
});

function Router() {
  return (
    <Shell>
      <Switch>
        <Route path="/" component={() => <Redirect to="/dashboard" />} />
        
        {/* Core Intelligence Routes */}
        <Route path="/dashboard" component={Dashboard} />
        <Route path="/hotspot-map" component={HotspotMap} />
        <Route path="/prevention" component={Prevention} />
        <Route path="/patterns" component={Patterns} />
        <Route path="/early-warning" component={EarlyWarning} />
        
        {/* Investigation Routes */}
        <Route path="/knowledge-graph" component={KnowledgeGraph} />
        <Route path="/knowledge-graph-ksp" component={KnowledgeGraphKsp} />
        <Route path="/evidence" component={EvidenceHub} />
        <Route path="/cases/:id" component={CaseEvidence} />
        <Route path="/replay" component={Replay} />
        <Route path="/agent" component={Agent} />
        <Route path="/ai" component={AiAssistant} />
        
        {/* Trust & Oversight Routes */}
        <Route path="/trust" component={Trust} />
        <Route path="/identity" component={Identity} />
        <Route path="/blockchain" component={Blockchain} />
        <Route path="/bias-audit" component={BiasAudit} />
        
        {/* System Settings */}
        <Route path="/settings" component={Settings} />
        
        {/* Fallback */}
        <Route>
          <div className="flex flex-col items-center justify-center h-[60vh]">
            <h1 className="text-[24px] font-display mb-2">404 - Not Found</h1>
            <p className="text-[var(--ink-secondary)]">The requested module does not exist.</p>
          </div>
        </Route>
      </Switch>
    </Shell>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <IntelProvider>
          <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, '')}>
            <Router />
          </WouterRouter>
        </IntelProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;

