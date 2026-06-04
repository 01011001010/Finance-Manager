CREATE EXTENSION IF NOT EXISTS CITEXT;

CREATE SCHEMA finance;

CREATE TABLE IF NOT EXISTS finance.accounts (
  id_a SERIAL PRIMARY KEY,
  account TEXT NOT NULL,
  currency CHAR(3) NOT NULL,
  archived BOOLEAN NOT NULL DEFAULT FALSE,
  CONSTRAINT unique_account_details UNIQUE (account, currency)
);


CREATE TABLE IF NOT EXISTS finance.transactions (
  id_t SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  pinned BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO finance.transactions (title, id_t)
VALUES
  ('Account opening balance', 1);  -- special id_t
  -- TODO idea: have a separate table, and provide a combined view, but separate inserts

-- Advance the internal key sequence to continue from 10 on the next insert
SELECT setval(pg_get_serial_sequence('finance.transactions', 'id_t'), 9);


CREATE TABLE IF NOT EXISTS finance.tags (
  tag SERIAL PRIMARY KEY,
  tag_name CITEXT NOT NULL,
  archived BOOLEAN NOT NULL DEFAULT FALSE,
  parent_tag INTEGER DEFAULT NULL REFERENCES finance.tags (tag),
  CONSTRAINT unique_tag_per_parent UNIQUE NULLS NOT DISTINCT (tag_name, parent_tag)
);

CREATE OR REPLACE FUNCTION finance.check_tag_nesting_limit()
RETURNS TRIGGER AS $$
BEGIN
  -- Cannot be own parent
  IF NEW.parent_tag = NEW.tag THEN
    RAISE EXCEPTION 'A tag cannot be its own parent.' USING ERRCODE = 'check_violation';
  END IF;
  IF NEW.parent_tag IS NOT NULL THEN
    -- Child cannot become parent
    IF EXISTS (SELECT 1
               FROM finance.tags
               WHERE tag = NEW.parent_tag
                 AND parent_tag IS NOT NULL
    ) THEN
      RAISE EXCEPTION 'Invalid Nesting: Tag % is already a child. You cannot nest further.', NEW.parent_tag USING ERRCODE = 'integrity_constraint_violation';
    END IF;
    -- Tag with children cannot change into a child
    IF EXISTS (SELECT 1
               FROM finance.tags
               WHERE parent_tag = NEW.tag
    ) THEN
      RAISE EXCEPTION 'Invalid Nesting: Tag % is already a parent. It cannot be nested under another tag.', NEW.tag USING ERRCODE = 'integrity_constraint_violation';
    END IF;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_tag_nesting
BEFORE INSERT OR UPDATE ON finance.tags
FOR EACH ROW
EXECUTE FUNCTION finance.check_tag_nesting_limit();

CREATE VIEW finance.tagsWithFullName AS  -- TODO rename this to tags, and original tags to some raw tags
SELECT
    t.tag,
    t.tag_name,
    t.archived,
    t.parent_tag,
    COALESCE(parent.tag_name || ' / ' || t.tag_name, t.tag_name) AS full_tag_name
FROM finance.tags t
LEFT JOIN finance.tags parent ON t.parent_tag = parent.tag;


CREATE TABLE IF NOT EXISTS finance.deltas (
  id_d SERIAL PRIMARY KEY,
  subtitle TEXT,
  ts_log TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  ts_analytics TIMESTAMPTZ DEFAULT NULL,
  ts TIMESTAMPTZ NOT NULL,
  amount NUMERIC(10, 2) NOT NULL,
  id_a INTEGER NOT NULL REFERENCES finance.accounts (id_a),
  tag INTEGER REFERENCES finance.tags (tag)
);


CREATE TABLE IF NOT EXISTS finance.deltasPerTransaction (
  id_t INTEGER NOT NULL REFERENCES finance.transactions (id_t),
  id_d INTEGER NOT NULL REFERENCES finance.deltas (id_d),
  PRIMARY KEY (id_t, id_d)
);


CREATE VIEW finance.deltasWithBalance AS
SELECT
  d.id_d,
  d.subtitle,
  d.ts_log,
  d.ts,
  d.ts_analytics,
  d.amount,
  d.id_a,
  d.tag,
  SUM(d.amount) OVER (PARTITION BY d.id_a ORDER BY d.ts ASC, d.id_d ASC) AS balance_after
FROM finance.deltas d
JOIN finance.accounts a ON d.id_a = a.id_a;


CREATE VIEW finance.completeDeltaInfo AS
SELECT t.id_t,
       t.title,
       t.pinned,
       d.subtitle,
       ta.full_tag_name,
       d.id_d,
       d.amount,
       a.id_a,
       a.currency,
       a.account,
       d.ts,
       d.ts_log,
       d.ts_analytics,
       d.balance_after
FROM finance.transactions t
JOIN finance.deltasPerTransaction dt ON dt.id_t = t.id_t
JOIN finance.deltasWithBalance d ON d.id_d = dt.id_d
JOIN finance.accounts a ON a.id_a = d.id_a
LEFT JOIN finance.tagsWithFullName ta ON ta.tag = d.tag;
