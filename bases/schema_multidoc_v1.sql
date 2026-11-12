-- ECU MEMS Manager SESSION / language-specific multi-document documentary schema.
-- Design foundation only. NOT the production Rover 482 layout.
-- Always set PRAGMA foreign_keys=ON on every SQLite connection.
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS documentary_database (
    singleton INTEGER NOT NULL PRIMARY KEY CHECK(singleton=1),
    schema_version INTEGER NOT NULL CHECK(schema_version=1),
    language TEXT NOT NULL
        CHECK(language IN ('fr','en','pt','es','it','de')),
    collection_revision INTEGER NOT NULL DEFAULT 1 CHECK(collection_revision>0)
);

CREATE TABLE IF NOT EXISTS documentary_documents (
    document_id TEXT NOT NULL CHECK(length(trim(document_id))>0),
    source_revision TEXT NOT NULL CHECK(length(trim(source_revision))>0),
    language TEXT NOT NULL
        CHECK(language IN ('fr','en','pt','es','it','de')),
    publisher TEXT NOT NULL DEFAULT '',
    edition_code TEXT NOT NULL CHECK(length(trim(edition_code))>0),
    source_filename TEXT NOT NULL CHECK(length(trim(source_filename))>0),
    source_format TEXT NOT NULL DEFAULT 'PDF',
    source_sha256 TEXT NOT NULL CHECK(
        length(source_sha256)=64
        AND source_sha256 NOT GLOB '*[^0-9a-f]*'
    ),
    source_pages INTEGER CHECK(source_pages IS NULL OR source_pages>0),
    vehicle_scope TEXT NOT NULL DEFAULT '',
    engine_scope TEXT NOT NULL DEFAULT '',
    ecu_scope TEXT NOT NULL DEFAULT '',
    release_rights TEXT NOT NULL DEFAULT 'unverified'
        CHECK(release_rights IN ('unverified','redistribution_permitted')),
    PRIMARY KEY(document_id,source_revision)
);

-- Every document has to match the single language declared by the DB.
-- Missing DB metadata is also rejected (fail closed).
CREATE TRIGGER IF NOT EXISTS documentary_language_insert
BEFORE INSERT ON documentary_documents
BEGIN
    SELECT CASE WHEN COALESCE(
        (SELECT language FROM documentary_database WHERE singleton=1),''
    ) <> NEW.language
    THEN RAISE(ABORT, 'DOCUMENT_LANGUAGE_DOES_NOT_MATCH_DATABASE') END;
END;

CREATE TRIGGER IF NOT EXISTS documentary_language_update
BEFORE UPDATE OF language ON documentary_documents
BEGIN
    SELECT RAISE(ABORT, 'DOCUMENT_LANGUAGE_IMMUTABLE');
END;

CREATE TRIGGER IF NOT EXISTS documentary_database_language_update
BEFORE UPDATE OF language ON documentary_database
WHEN EXISTS(SELECT 1 FROM documentary_documents)
BEGIN
    SELECT RAISE(ABORT, 'DATABASE_LANGUAGE_IMMUTABLE_WITH_DOCUMENTS');
END;

-- A source edition is immutable: new PDFs are a NEW source_revision.
CREATE TRIGGER IF NOT EXISTS documentary_source_identity_update
BEFORE UPDATE OF document_id,source_revision,source_sha256,edition_code
ON documentary_documents
BEGIN
    SELECT RAISE(ABORT, 'DOCUMENT_SOURCE_IDENTITY_IMMUTABLE');
END;

-- Source sections are scoped by document and source edition.
CREATE TABLE IF NOT EXISTS documentary_sections (
    document_id TEXT NOT NULL,
    source_revision TEXT NOT NULL,
    section_id TEXT NOT NULL CHECK(length(trim(section_id))>0),
    reference_code TEXT NOT NULL DEFAULT '',
    title TEXT NOT NULL CHECK(length(trim(title))>0),
    page_first INTEGER CHECK(page_first IS NULL OR page_first>0),
    page_last INTEGER CHECK(page_last IS NULL OR page_last>0),
    CHECK(page_first IS NULL OR page_last IS NULL OR page_first<=page_last),
    PRIMARY KEY(document_id,source_revision,section_id),
    FOREIGN KEY(document_id,source_revision)
       REFERENCES documentary_documents(document_id,source_revision)
       ON DELETE RESTRICT ON UPDATE RESTRICT
);

-- Entries can represent individual instructions, cautions, data or figures.
-- Every entry belongs to one source edition. No globally ambiguous "12.65.12".
CREATE TABLE IF NOT EXISTS documentary_entries (
    document_id TEXT NOT NULL,
    source_revision TEXT NOT NULL,
    entry_id TEXT NOT NULL CHECK(length(trim(entry_id))>0),
    section_id TEXT,
    entry_type TEXT NOT NULL CHECK(
        entry_type IN ('procedure','step','notice','technical_value',
                       'figure','page_text','reference','other')
    ),
    manufacturer_reference TEXT NOT NULL DEFAULT '',
    source_page INTEGER CHECK(source_page IS NULL OR source_page>0),
    source_text TEXT NOT NULL CHECK(length(trim(source_text))>0),
    vehicle_scope TEXT NOT NULL DEFAULT '',
    engine_scope TEXT NOT NULL DEFAULT '',
    ecu_scope TEXT NOT NULL DEFAULT '',
    verification_status TEXT NOT NULL DEFAULT 'review_required'
        CHECK(verification_status IN ('review_required','source_checked',
                                      'technical_reviewed')),
    PRIMARY KEY(document_id,source_revision,entry_id),
    FOREIGN KEY(document_id,source_revision)
       REFERENCES documentary_documents(document_id,source_revision)
       ON DELETE RESTRICT ON UPDATE RESTRICT,
    FOREIGN KEY(document_id,source_revision,section_id)
       REFERENCES documentary_sections(document_id,source_revision,section_id)
       ON DELETE RESTRICT ON UPDATE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_doc_sections_reference
    ON documentary_sections(document_id,source_revision,reference_code);
CREATE INDEX IF NOT EXISTS idx_doc_entries_reference
    ON documentary_entries(manufacturer_reference,document_id,source_revision);
CREATE INDEX IF NOT EXISTS idx_doc_entries_page
    ON documentary_entries(document_id,source_revision,source_page);

-- Deleting a published source is never an implicit part of importing a new PDF.
-- Importers must use a transaction on a temporary copy, verify the full
-- snapshot, then atomically replace the installed language pack.
