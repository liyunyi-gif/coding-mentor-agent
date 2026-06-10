MIGRATIONS: list[tuple[str, str]] = [
    ("001_initial", """
        CREATE TABLE IF NOT EXISTS agent_sessions (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL DEFAULT 'active',
            started_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS session_turns (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL REFERENCES agent_sessions(id),
            status TEXT NOT NULL DEFAULT 'streaming',
            user_message_summary TEXT,
            code_ref TEXT,
            assistant_message_summary TEXT,
            started_at TEXT NOT NULL DEFAULT (datetime('now')),
            ended_at TEXT
        );

        CREATE TABLE IF NOT EXISTS session_messages (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            turn_id TEXT NOT NULL REFERENCES session_turns(id),
            message_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content_text TEXT NOT NULL,
            code_ref TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS session_sse_events (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            turn_id TEXT,
            seq INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS intent_routes (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            turn_id TEXT NOT NULL REFERENCES session_turns(id),
            intent TEXT NOT NULL,
            confidence REAL NOT NULL DEFAULT 0,
            target_concept_ids_json TEXT DEFAULT '[]',
            evidence_signals_json TEXT DEFAULT '[]',
            has_code INTEGER DEFAULT 0,
            allowed_tool_group TEXT DEFAULT 'read_only_tools',
            risk_flags_json TEXT DEFAULT '[]',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS tool_evidence (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            turn_id TEXT,
            tool_name TEXT NOT NULL,
            tool_call_id TEXT,
            result_code TEXT NOT NULL,
            summary_json TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS concepts (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            unit_id TEXT,
            order_index INTEGER DEFAULT 0,
            content_md TEXT,
            summary_md TEXT,
            prerequisites_json TEXT DEFAULT '[]'
        );

        CREATE TABLE IF NOT EXISTS course_units (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            order_index INTEGER DEFAULT 0,
            concept_ids_json TEXT DEFAULT '[]'
        );

        CREATE TABLE IF NOT EXISTS exercises (
            id TEXT PRIMARY KEY,
            concept_ids_json TEXT DEFAULT '[]',
            title TEXT NOT NULL,
            prompt_md TEXT NOT NULL,
            difficulty INTEGER DEFAULT 1,
            starter_code TEXT,
            visible_examples_json TEXT DEFAULT '[]',
            acceptance_checklist_json TEXT DEFAULT '[]',
            review_rubric TEXT
        );

        CREATE TABLE IF NOT EXISTS diagnostic_sessions (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            started_at TEXT NOT NULL DEFAULT (datetime('now')),
            completed_at TEXT
        );

        CREATE TABLE IF NOT EXISTS diagnostic_answers (
            id TEXT PRIMARY KEY,
            diagnostic_session_id TEXT NOT NULL REFERENCES diagnostic_sessions(id),
            concept_id TEXT,
            question_json TEXT NOT NULL,
            answer_json TEXT NOT NULL,
            is_correct INTEGER,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS diagnostic_concept_state (
            diagnostic_session_id TEXT NOT NULL,
            concept_id TEXT NOT NULL,
            mastery INTEGER DEFAULT 0,
            confidence REAL DEFAULT 0,
            evidence_count INTEGER DEFAULT 0,
            band TEXT DEFAULT 'learning',
            conflicting_evidence_count INTEGER DEFAULT 0,
            PRIMARY KEY (diagnostic_session_id, concept_id)
        );

        CREATE TABLE IF NOT EXISTS practice_contracts (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            turn_id TEXT,
            concept_ids_json TEXT DEFAULT '[]',
            title TEXT NOT NULL,
            prompt_md TEXT NOT NULL,
            starter_code TEXT,
            expected_behavior TEXT,
            visible_examples_json TEXT DEFAULT '[]',
            acceptance_checklist_json TEXT DEFAULT '[]',
            review_rubric TEXT,
            difficulty INTEGER DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS practice_submissions (
            id TEXT PRIMARY KEY,
            practice_contract_id TEXT NOT NULL REFERENCES practice_contracts(id),
            session_id TEXT NOT NULL,
            turn_id TEXT,
            code TEXT NOT NULL,
            review_status TEXT,
            review_confidence TEXT,
            review_summary TEXT,
            progress_effect TEXT DEFAULT 'not_recorded',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS learning_events (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            turn_id TEXT,
            event_type TEXT NOT NULL,
            concept_ids_json TEXT DEFAULT '[]',
            summary TEXT,
            evidence_json TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS concept_mastery (
            session_id TEXT NOT NULL,
            concept_id TEXT NOT NULL,
            mastery_level INTEGER DEFAULT 0,
            confidence REAL DEFAULT 0,
            evidence_count INTEGER DEFAULT 0,
            review_priority INTEGER DEFAULT 0,
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (session_id, concept_id)
        );

        CREATE TABLE IF NOT EXISTS local_profile (
            id TEXT PRIMARY KEY DEFAULT 'local',
            profile_json TEXT DEFAULT '{}'
        );

        INSERT OR IGNORE INTO local_profile(id, profile_json)
        VALUES ('local', '{"profile_summary":"Python 课程学习者。","current_level":"未诊断"}');

        CREATE INDEX IF NOT EXISTS idx_turns_session ON session_turns(session_id);
        CREATE INDEX IF NOT EXISTS idx_messages_turn ON session_messages(turn_id);
        CREATE INDEX IF NOT EXISTS idx_sse_session_seq ON session_sse_events(session_id, seq);
        CREATE INDEX IF NOT EXISTS idx_tool_evidence_session ON tool_evidence(session_id);
        CREATE INDEX IF NOT EXISTS idx_concepts_unit ON concepts(unit_id);
        CREATE INDEX IF NOT EXISTS idx_exercises_concepts ON exercises(concept_ids_json);
        CREATE INDEX IF NOT EXISTS idx_practice_contracts_session ON practice_contracts(session_id);
        CREATE INDEX IF NOT EXISTS idx_learning_events_session ON learning_events(session_id);
        CREATE INDEX IF NOT EXISTS idx_concept_mastery_session ON concept_mastery(session_id);
    """),
]
