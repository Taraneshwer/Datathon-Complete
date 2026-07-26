
import { 
  ListCasesParams, ListHotspotsParams, ListAlertsParams, 
  ListAccessLogParams, ListGraphNodesParams, ListGraphEdgesParams, ListSuspectsParams, ListVictimsParams 
} from '@/api-client';

// The api layer intercepts the orval generated hooks by rewriting the base url.
// Wait, the prompt says: "The backend will serve real mock data from these endpoints. Wire the hooks to the backend (not to mockData directly from components) — the custom fetch layer in the api-client handles the base URL."
// So I don't need to intercept here, I just use the hooks from @/api-client.
// Wait, the prompt also says: "Structure fetching like this pattern (swappable): export async function fetchCases(params?) { return mockCases... }"
// Actually, it says: "Structure fetching like this pattern (swappable)... Use this approach for all data — NOT direct imports from mockData into components."
// BUT it also says: "API HOOKS — import from @/api-client... Available hooks (use ALL of them throughout the app)... The backend will serve real mock data from these endpoints. Wire the hooks to the backend (not to mockData directly from components)"
// This is slightly conflicting. If the backend serves it, I don't need a custom fetch layer for the frontend to return `mockData`.
// Wait, "The backend will serve real mock data from these endpoints. Wire the hooks to the backend ... the custom fetch layer in the api-client handles the base URL."
// Okay, so I MUST use the generated hooks directly, like `useListCases()`.
// I will just create `src/api/index.ts` to export them if needed, or just import them directly in components.
// I will import from `@/api-client` in components directly as instructed.

// However, the prompt also says: "Create src/mockData/index.ts as THE single shared dataset. Every module reads from this. Structure it so fetch calls can swap in real API endpoints with zero component changes."
// This implies the backend might NOT be ready or we might be using swappable functions if the hooks fail?
// Let's stick to the generated hooks, but if the backend is just a mock server, the hooks will fetch from it.
// If the prompt says "Available hooks (use ALL of them throughout the app): useHealthCheck()...", I will use them.

// To be safe, I'll use the generated hooks from @/api-client.
