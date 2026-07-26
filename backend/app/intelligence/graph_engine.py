"""
app/intelligence/graph_engine.py
─────────────────────────────────────────────────────────────────────────────
100% Zoho Catalyst-Native Relational Graph Engine.
Replaces Neo4j Aura Cloud by executing Breadth-First Search (BFS), Depth-First
Search (DFS), Shortest Path, Community Detection, and Relationship Traversal
over indexed Data Store SQL tables (Person, Vehicle, Weapon, Relationship, etc.).
─────────────────────────────────────────────────────────────────────────────
"""
import logging
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Set, Tuple
from app.db.catalyst import CatalystDBClient, get_datastore

logger = logging.getLogger(__name__)

class CatalystRelationalGraphEngine:
    """
    100% Catalyst-Native Graph Engine replacing Neo4j Aura Cloud.
    Executes BFS, DFS, Shortest Path, and Community Detection over indexed Data Store SQL tables.
    """
    def __init__(self, db_client: Optional[CatalystDBClient] = None):
        self.db = db_client or CatalystDBClient()
        self.cache = self.db.get_cache_service()

    def _fetch_adjacency_list(self, max_confidence_threshold: float = 0.50) -> Dict[str, List[Tuple[str, str, float]]]:
        """Fetches graph edges from Data Store Relationship table into memory for high-speed traversal."""
        try:
            sql = f"SELECT source_entity_id, target_entity_id, relationship_type, confidence FROM Relationship WHERE confidence >= {max_confidence_threshold}"
            rows = self.db.execute_sql_query(sql)
        except Exception as e:
            logger.warning(f"Failed to fetch SQL graph relationships (fallback to empty graph): {e}")
            rows = []

        adj = defaultdict(list)
        for row in rows:
            src = str(row.get("source_entity_id", ""))
            tgt = str(row.get("target_entity_id", ""))
            rel = str(row.get("relationship_type", "ASSOCIATED_WITH"))
            conf = float(row.get("confidence", 1.0))
            if src and tgt:
                adj[src].append((tgt, rel, conf))
                adj[tgt].append((src, f"INVERSE_{rel}", conf))
        return adj

    def breadth_first_search(self, start_entity_id: str, max_depth: int = 3) -> List[Dict[str, Any]]:
        """
        Executes Breadth-First Search (BFS) to discover criminal networks up to N hops away.
        """
        cache_key = f"graph:bfs:{start_entity_id}:depth{max_depth}"
        try:
            cached = self.cache.get(cache_key)
            if cached:
                return eval(cached)
        except Exception:
            pass

        adj = self._fetch_adjacency_list()
        visited: Set[str] = {start_entity_id}
        queue: deque[Tuple[str, int, List[Dict[str, Any]]]] = deque([(start_entity_id, 0, [])])
        discovered_paths = []

        while queue:
            curr_id, depth, path = queue.popleft()
            if depth > max_depth:
                continue
            if depth > 0:
                discovered_paths.append({"entity_id": curr_id, "depth": depth, "path": path})

            if depth < max_depth:
                for neighbor_id, rel_type, conf in adj.get(curr_id, []):
                    if neighbor_id not in visited:
                        visited.add(neighbor_id)
                        new_step = {"from": curr_id, "to": neighbor_id, "rel": rel_type, "confidence": conf}
                        queue.append((neighbor_id, depth + 1, path + [new_step]))

        try:
            self.cache.put(cache_key, str(discovered_paths), ttl=43200) # Cache for 12 hours
        except Exception:
            pass
        return discovered_paths

    def depth_first_search(self, current_id: str, target_type: str, visited: Optional[Set[str]] = None, depth: int = 0, max_depth: int = 4) -> List[str]:
        """
        Executes Depth-First Search (DFS) to trace linear criminal chains.
        """
        if visited is None:
            visited = set()
        visited.add(current_id)

        if depth >= max_depth:
            return []

        adj = self._fetch_adjacency_list()
        results = []
        for neighbor_id, rel_type, _ in adj.get(current_id, []):
            if neighbor_id not in visited:
                entity_type = self._get_entity_type(neighbor_id)
                if entity_type == target_type:
                    results.append(neighbor_id)
                results.extend(self.depth_first_search(neighbor_id, target_type, visited, depth + 1, max_depth))
        return results

    def shortest_path(self, source_id: str, target_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Calculates the shortest criminal relationship path between two entities.
        """
        adj = self._fetch_adjacency_list()
        queue: deque[Tuple[str, List[Dict[str, Any]]]] = deque([(source_id, [])])
        visited: Set[str] = {source_id}

        while queue:
            curr_id, path = queue.popleft()
            if curr_id == target_id:
                return path

            for neighbor_id, rel_type, conf in adj.get(curr_id, []):
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    step = {"from": curr_id, "to": neighbor_id, "rel": rel_type, "confidence": conf}
                    queue.append((neighbor_id, path + [step]))
        return None

    def community_grouping_connected_components(self) -> List[Set[str]]:
        """
        Executes Connected Components graph algorithm to group isolated criminal syndicates.
        """
        adj = self._fetch_adjacency_list()
        visited: Set[str] = set()
        syndicates: List[Set[str]] = []

        for node in list(adj.keys()):
            if node not in visited:
                component: Set[str] = set()
                queue: deque[str] = deque([node])
                visited.add(node)
                while queue:
                    curr = queue.popleft()
                    component.add(curr)
                    for nxt, _, _ in adj.get(curr, []):
                        if nxt not in visited:
                            visited.add(nxt)
                            queue.append(nxt)
                if len(component) >= 2:
                    syndicates.append(component)
        return syndicates

    def _get_entity_type(self, entity_id: str) -> str:
        """Helper to resolve entity table type from ID prefix."""
        if entity_id.startswith("per_") or "crim" in entity_id: return "PERSON"
        if entity_id.startswith("veh_") or "DL-" in entity_id: return "VEHICLE"
        if entity_id.startswith("wea_") or "pistol" in entity_id.lower(): return "WEAPON"
        if entity_id.startswith("org_") or "synd" in entity_id.lower(): return "ORGANIZATION"
        if entity_id.startswith("loc_") or "sector" in entity_id.lower(): return "LOCATION"
        return "UNKNOWN"

# Singleton export
graph_engine = CatalystRelationalGraphEngine()
