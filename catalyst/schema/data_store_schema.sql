-- ============================================================================
-- PROJECT RAINFALL: 100% ZOHO CATALYST DATA STORE SCHEMA (SQL DDL)
-- Complete schema for 15 Core Application Tables + 7 Relational Graph Tables.
-- Replaces MongoDB, Neo4j, and Qdrant relational/graph metadata storage.
-- ============================================================================

-- ── CORE APPLICATION TABLES (15) ────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS Users (
    user_id VARCHAR(64) PRIMARY KEY,
    username VARCHAR(128) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(64) NOT NULL DEFAULT 'INVESTIGATOR',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Officers (
    officer_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) REFERENCES Users(user_id),
    badge_number VARCHAR(64) UNIQUE NOT NULL,
    rank VARCHAR(64) NOT NULL,
    station_code VARCHAR(64) NOT NULL,
    district_id VARCHAR(64) NOT NULL,
    clearance_level INT DEFAULT 1,
    contact_phone VARCHAR(32),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS PoliceStations (
    station_code VARCHAR(64) PRIMARY KEY,
    station_name VARCHAR(255) NOT NULL,
    district_id VARCHAR(64) NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    contact_email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Districts (
    district_id VARCHAR(64) PRIMARY KEY,
    district_name VARCHAR(128) UNIQUE NOT NULL,
    state_name VARCHAR(128) DEFAULT 'Karnataka',
    zone VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS CrimeCategories (
    category_code VARCHAR(64) PRIMARY KEY,
    category_name VARCHAR(128) UNIQUE NOT NULL,
    default_severity VARCHAR(32) DEFAULT 'MEDIUM',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS FIR (
    fir_number VARCHAR(64) PRIMARY KEY,
    station_code VARCHAR(64) REFERENCES PoliceStations(station_code),
    incident_datetime TIMESTAMP NOT NULL,
    reported_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(32) DEFAULT 'MEDIUM',
    crime_category_code VARCHAR(64) REFERENCES CrimeCategories(category_code),
    status VARCHAR(64) DEFAULT 'REGISTERED',
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    h3_index VARCHAR(32),
    reporting_officer_id VARCHAR(64) REFERENCES Officers(officer_id),
    blockchain_tx_hash VARCHAR(128),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Cases (
    case_id VARCHAR(64) PRIMARY KEY,
    fir_number VARCHAR(64) REFERENCES FIR(fir_number),
    case_title VARCHAR(255) NOT NULL,
    assigned_officer_id VARCHAR(64) REFERENCES Officers(officer_id),
    investigation_status VARCHAR(64) DEFAULT 'OPEN',
    priority VARCHAR(32) DEFAULT 'NORMAL',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS EvidenceMetadata (
    evidence_id VARCHAR(64) PRIMARY KEY,
    case_id VARCHAR(64) REFERENCES Cases(case_id),
    evidence_type VARCHAR(64) NOT NULL, -- IMAGE, VIDEO, AUDIO, DOCUMENT
    file_reference VARCHAR(512) NOT NULL, -- Catalyst Stratus URL
    description TEXT,
    collected_by VARCHAR(64) REFERENCES Officers(officer_id),
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    chain_of_custody_hash VARCHAR(128),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Reports (
    report_id VARCHAR(64) PRIMARY KEY,
    case_id VARCHAR(64) REFERENCES Cases(case_id),
    author_id VARCHAR(64) REFERENCES Officers(officer_id),
    report_type VARCHAR(64) NOT NULL, -- FINAL_CHARGESHEET, AI_SUMMARY, FORENSIC
    title VARCHAR(255) NOT NULL,
    stratus_file_reference VARCHAR(512),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Assignments (
    assignment_id VARCHAR(64) PRIMARY KEY,
    case_id VARCHAR(64) REFERENCES Cases(case_id),
    officer_id VARCHAR(64) REFERENCES Officers(officer_id),
    role_in_case VARCHAR(64) DEFAULT 'LEAD_INVESTIGATOR',
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Notifications (
    notification_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) REFERENCES Users(user_id),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS AuditLogs (
    log_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64),
    action_type VARCHAR(64) NOT NULL,
    target_entity VARCHAR(128),
    ip_address VARCHAR(64),
    detail TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Roles (
    role_id VARCHAR(64) PRIMARY KEY,
    role_name VARCHAR(64) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS Permissions (
    permission_id VARCHAR(64) PRIMARY KEY,
    role_id VARCHAR(64) REFERENCES Roles(role_id),
    resource VARCHAR(128) NOT NULL,
    can_read BOOLEAN DEFAULT FALSE,
    can_write BOOLEAN DEFAULT FALSE,
    can_delete BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS Sessions (
    session_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) REFERENCES Users(user_id),
    refresh_token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── RELATIONAL GRAPH ENTITY & EDGE TABLES (7) ───────────────────────────────
-- Replaces Neo4j Aura Cloud node and relationship storage.

CREATE TABLE IF NOT EXISTS Person (
    person_id VARCHAR(64) PRIMARY KEY,
    national_id VARCHAR(64),
    full_name VARCHAR(255) NOT NULL,
    alias_name VARCHAR(255),
    date_of_birth DATE,
    known_addresses TEXT,
    criminal_record_status VARCHAR(64) DEFAULT 'NONE', -- NONE, SUSPECT, WANTED, CONVICTED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Vehicle (
    vehicle_id VARCHAR(64) PRIMARY KEY,
    license_plate VARCHAR(64) UNIQUE NOT NULL,
    make_model VARCHAR(128),
    color VARCHAR(64),
    registered_owner_id VARCHAR(64) REFERENCES Person(person_id),
    status VARCHAR(64) DEFAULT 'CLEAR', -- CLEAR, STOLEN, WANTED_IN_CRIME
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Phone (
    phone_id VARCHAR(64) PRIMARY KEY,
    phone_number VARCHAR(64) UNIQUE NOT NULL,
    subscriber_name VARCHAR(255),
    carrier VARCHAR(64),
    associated_person_id VARCHAR(64) REFERENCES Person(person_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Weapon (
    weapon_id VARCHAR(64) PRIMARY KEY,
    serial_number VARCHAR(128) UNIQUE,
    weapon_type VARCHAR(64) NOT NULL, -- FIREARM, BLADED, EXPLOSIVE, BLUNT
    manufacturer VARCHAR(128),
    status VARCHAR(64) DEFAULT 'UNRECOVERED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Location (
    location_id VARCHAR(64) PRIMARY KEY,
    location_name VARCHAR(255) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    h3_index VARCHAR(32),
    address TEXT,
    district_id VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Organization (
    org_id VARCHAR(64) PRIMARY KEY,
    org_name VARCHAR(255) UNIQUE NOT NULL,
    org_type VARCHAR(64) NOT NULL, -- LEGITIMATE_BUSINESS, CRIMINAL_SYNDICATE, SHELL_COMPANY
    registration_number VARCHAR(128),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Relationship (
    relationship_id VARCHAR(64) PRIMARY KEY,
    source_entity_id VARCHAR(64) NOT NULL,
    source_entity_type VARCHAR(64) NOT NULL, -- PERSON, VEHICLE, PHONE, WEAPON, LOCATION, ORG, CASE
    target_entity_id VARCHAR(64) NOT NULL,
    target_entity_type VARCHAR(64) NOT NULL,
    relationship_type VARCHAR(64) NOT NULL, -- ASSOCIATED_WITH, USED_IN, OWNS, CALLED, VISITED_IN, MEMBER_OF, INVOLVED_IN
    confidence DOUBLE PRECISION DEFAULT 1.0, -- 0.0 to 1.0 AI confidence score
    supporting_case_id VARCHAR(64) REFERENCES Cases(case_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexing for High-Speed SQL BFS/DFS Graph Traversal
CREATE INDEX IF NOT EXISTS idx_rel_source ON Relationship(source_entity_id, relationship_type);
CREATE INDEX IF NOT EXISTS idx_rel_target ON Relationship(target_entity_id, relationship_type);
CREATE INDEX IF NOT EXISTS idx_fir_h3 ON FIR(h3_index);
CREATE INDEX IF NOT EXISTS idx_case_status ON Cases(investigation_status, priority);
