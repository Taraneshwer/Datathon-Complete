"""
app/services/graph_service.py
─────────────────────────────────────────────────────────────────────────────
Neo4j Knowledge Graph Service.

Handles all Cypher writes and reads for the crime knowledge graph.

Node types: Criminal, Victim, Witness, Officer, Vehicle, Weapon,
            Location, Organization, FinancialAccount, DigitalEvidence, Case

Relationships: ASSOCIATED_WITH, USED_IN, VISITED_IN, OWNS, CALLED,
               WITNESSED, INVESTIGATED, TRANSFERRED_TO, MEMBER_OF
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
from typing import Any

from neo4j import AsyncDriver

from app.models.schemas import GraphEntities

logger = logging.getLogger(__name__)


class GraphService:
    """Encapsulates all Neo4j Cypher write and read operations."""

    def __init__(self, driver: AsyncDriver) -> None:
        self._driver = driver

    # ── Core Write ────────────────────────────────────────────────────────────

    async def write_case_graph(
        self,
        fir_number: str,
        case_id: str,
        entities: GraphEntities,
    ) -> int:
        """
        Write all graph entities and relationships for a FIR.
        Uses MERGE to ensure idempotency — safe to call multiple times.
        Returns total nodes created.
        """
        total_created = 0
        async with self._driver.session() as session:

            # ── Case node ─────────────────────────────────────────────────────
            await session.run(
                """
                MERGE (c:Case {fir_number: $fir_number})
                ON CREATE SET c.case_id = $case_id, c.created_at = datetime()
                ON MATCH  SET c.updated_at = datetime()
                """,
                fir_number=fir_number, case_id=case_id,
            )

            # ── Criminals ─────────────────────────────────────────────────────
            for cr in entities.criminals:
                r = await session.run(
                    """
                    MERGE (n:Criminal {national_id: $nid})
                    ON CREATE SET n.name=$name, n.alias=$alias,
                                  n.known_addresses=$addrs, n.created_at=datetime()
                    ON MATCH  SET n.name=$name, n.updated_at=datetime()
                    WITH n
                    MATCH (c:Case {fir_number: $fir})
                    MERGE (n)-[r:ASSOCIATED_WITH]->(c)
                    ON CREATE SET r.since=datetime()
                    RETURN n
                    """,
                    nid=cr.national_id or cr.name,
                    name=cr.name, alias=cr.alias,
                    addrs=cr.known_addresses, fir=fir_number,
                )
                total_created += (await r.consume()).counters.nodes_created

            # ── Victims ──────────────────────────────────────────────────────
            for v in entities.victims:
                r = await session.run(
                    """
                    MERGE (n:Victim {victim_id: $vid})
                    ON CREATE SET n.name=$name, n.age=$age,
                                  n.contact=$contact, n.created_at=datetime()
                    WITH n
                    MATCH (c:Case {fir_number: $fir})
                    MERGE (n)-[r:VICTIM_IN]->(c)
                    ON CREATE SET r.since=datetime()
                    RETURN n
                    """,
                    vid=v.victim_id or v.name,
                    name=v.name, age=v.age,
                    contact=v.contact, fir=fir_number,
                )
                total_created += (await r.consume()).counters.nodes_created

            # ── Witnesses ─────────────────────────────────────────────────────
            for w in entities.witnesses:
                r = await session.run(
                    """
                    MERGE (n:Witness {witness_id: $wid})
                    ON CREATE SET n.name=$name, n.statement_summary=$stmt,
                                  n.created_at=datetime()
                    WITH n
                    MATCH (c:Case {fir_number: $fir})
                    MERGE (n)-[r:WITNESSED]->(c)
                    ON CREATE SET r.since=datetime()
                    RETURN n
                    """,
                    wid=w.witness_id or w.name,
                    name=w.name, stmt=w.statement_summary, fir=fir_number,
                )
                total_created += (await r.consume()).counters.nodes_created

            # ── Vehicles ──────────────────────────────────────────────────────
            for v in entities.vehicles:
                r = await session.run(
                    """
                    MERGE (n:Vehicle {registration_number: $reg})
                    ON CREATE SET n.make=$make, n.model=$model,
                                  n.color=$color, n.created_at=datetime()
                    WITH n
                    MATCH (c:Case {fir_number: $fir})
                    MERGE (n)-[r:USED_IN]->(c) ON CREATE SET r.since=datetime()
                    RETURN n
                    """,
                    reg=v.registration_number,
                    make=v.make, model=v.model, color=v.color, fir=fir_number,
                )
                total_created += (await r.consume()).counters.nodes_created

            # ── Locations ─────────────────────────────────────────────────────
            for loc in entities.locations:
                r = await session.run(
                    """
                    MERGE (n:Location {name: $name})
                    ON CREATE SET n.latitude=$lat, n.longitude=$lon,
                                  n.address=$addr, n.created_at=datetime()
                    WITH n
                    MATCH (c:Case {fir_number: $fir})
                    MERGE (n)-[r:VISITED_IN]->(c) ON CREATE SET r.since=datetime()
                    RETURN n
                    """,
                    name=loc.name, lat=loc.latitude,
                    lon=loc.longitude, addr=loc.address, fir=fir_number,
                )
                total_created += (await r.consume()).counters.nodes_created

            # ── Weapons ───────────────────────────────────────────────────────
            for w in entities.weapons:
                r = await session.run(
                    """
                    MERGE (n:Weapon {type: $type, serial_number: $serial})
                    ON CREATE SET n.description=$desc, n.created_at=datetime()
                    WITH n
                    MATCH (c:Case {fir_number: $fir})
                    MERGE (n)-[r:USED_IN]->(c) ON CREATE SET r.since=datetime()
                    RETURN n
                    """,
                    type=w.type, serial=w.serial_number or "UNKNOWN",
                    desc=w.description, fir=fir_number,
                )
                total_created += (await r.consume()).counters.nodes_created

            # ── Organizations ─────────────────────────────────────────────────
            for org in entities.organizations:
                r = await session.run(
                    """
                    MERGE (n:Organization {name: $name})
                    ON CREATE SET n.org_type=$otype, n.registration_id=$rid,
                                  n.created_at=datetime()
                    WITH n
                    MATCH (c:Case {fir_number: $fir})
                    MERGE (n)-[r:ASSOCIATED_WITH]->(c) ON CREATE SET r.since=datetime()
                    RETURN n
                    """,
                    name=org.name, otype=org.org_type,
                    rid=org.registration_id, fir=fir_number,
                )
                total_created += (await r.consume()).counters.nodes_created

            # ── Financial Accounts ────────────────────────────────────────────
            for acc in entities.financial_accounts:
                r = await session.run(
                    """
                    MERGE (n:FinancialAccount {account_number: $acno})
                    ON CREATE SET n.bank=$bank, n.account_type=$atype,
                                  n.created_at=datetime()
                    WITH n
                    MATCH (c:Case {fir_number: $fir})
                    MERGE (n)-[r:LINKED_TO]->(c) ON CREATE SET r.since=datetime()
                    RETURN n
                    """,
                    acno=acc.account_number, bank=acc.bank,
                    atype=acc.account_type, fir=fir_number,
                )
                total_created += (await r.consume()).counters.nodes_created

        logger.info(
            "GraphService: wrote %d nodes for FIR '%s'", total_created, fir_number
        )
        return total_created

    # ── Criminal–Vehicle link ─────────────────────────────────────────────────

    async def link_criminal_to_vehicle(
        self, criminal_national_id: str, vehicle_reg: str
    ) -> None:
        """Create an OWNS relationship between a criminal and a vehicle."""
        async with self._driver.session() as session:
            await session.run(
                """
                MATCH (cr:Criminal {national_id: $nid})
                MATCH (v:Vehicle {registration_number: $reg})
                MERGE (cr)-[r:OWNS]->(v)
                ON CREATE SET r.since=datetime()
                """,
                nid=criminal_national_id, reg=vehicle_reg,
            )

    # ── Read: RAG Context ─────────────────────────────────────────────────────

    async def get_case_context(self, fir_number: str, depth: int = 2) -> list[str]:
        """Retrieve human-readable entity paths for a case (used by RAG)."""
        async with self._driver.session() as session:
            result = await session.run(
                """
                MATCH path = (c:Case {fir_number: $fir})<-[*1..$depth]-(n)
                RETURN
                  [node in nodes(path) | COALESCE(
                    node.name, node.registration_number,
                    node.type, node.fir_number, node.account_number,
                    toString(id(node))
                  )] AS path_nodes,
                  [rel in relationships(path) | type(rel)] AS rel_types
                LIMIT 50
                """,
                fir=fir_number, depth=depth,
            )
            records = await result.data()

        paths: list[str] = []
        for rec in records:
            nodes: list[str] = rec.get("path_nodes", [])
            rels: list[str] = rec.get("rel_types", [])
            parts: list[str] = []
            for i, node in enumerate(nodes):
                parts.append(str(node))
                if i < len(rels):
                    parts.append(f"--[{rels[i]}]-->")
            paths.append(" ".join(parts))
        return paths

    # ── Read: Criminal Network ────────────────────────────────────────────────

    async def get_criminal_network(
        self, criminal_name: str, hops: int = 3
    ) -> list[dict[str, Any]]:
        """Find all entities connected to a criminal within N hops."""
        async with self._driver.session() as session:
            result = await session.run(
                """
                MATCH (cr:Criminal)-[*1..$hops]-(n)
                WHERE toLower(cr.name) CONTAINS toLower($name)
                RETURN labels(n)[0] AS node_type,
                       COALESCE(n.name, n.registration_number,
                                n.fir_number, toString(id(n))) AS entity,
                       cr.name AS criminal
                LIMIT 100
                """,
                name=criminal_name, hops=hops,
            )
            return await result.data()

    # ── Read: Financial transfers ─────────────────────────────────────────────

    async def find_financial_patterns(
        self, case_id: str
    ) -> list[dict[str, Any]]:
        """Identify financial account clusters associated with a case."""
        async with self._driver.session() as session:
            result = await session.run(
                """
                MATCH (c:Case {case_id: $case_id})<-[:LINKED_TO]-(f:FinancialAccount)
                OPTIONAL MATCH (f)-[:TRANSFERRED_TO]->(f2:FinancialAccount)
                RETURN f.account_number AS source,
                       f.bank AS source_bank,
                       collect(f2.account_number) AS transfers
                """,
                case_id=case_id,
            )
            return await result.data()

    # ── Read: Location proximity ──────────────────────────────────────────────

    async def find_location_cases(
        self, lat: float, lon: float, radius_deg: float = 0.1
    ) -> list[dict[str, Any]]:
        async with self._driver.session() as session:
            result = await session.run(
                """
                MATCH (l:Location)-[:VISITED_IN]->(c:Case)
                WHERE abs(l.latitude - $lat) < $r AND abs(l.longitude - $lon) < $r
                RETURN l.name AS location, l.latitude AS lat,
                       l.longitude AS lon, c.fir_number AS fir_number
                LIMIT 25
                """,
                lat=lat, lon=lon, r=radius_deg,
            )
            return await result.data()
