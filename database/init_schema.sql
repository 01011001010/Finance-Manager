CREATE EXTENSION IF NOT EXISTS CITEXT;


CREATE TABLE IF NOT EXISTS accounts (
  id_a SERIAL PRIMARY KEY,
  account TEXT NOT NULL,
  currency CHAR(3) NOT NULL,
  opening_balance NUMERIC(10, 2) NOT NULL DEFAULT 0,
  opened_ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  archived BOOLEAN NOT NULL DEFAULT FALSE,
  CONSTRAINT unique_account_details UNIQUE (account, currency)
);


CREATE TABLE IF NOT EXISTS transactions (
  id_t SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  pinned BOOLEAN NOT NULL DEFAULT FALSE
);


CREATE TABLE IF NOT EXISTS tags (
  tag SERIAL PRIMARY KEY,
  tag_name CITEXT NOT NULL,
  archived BOOLEAN NOT NULL DEFAULT FALSE,
  parent_tag INTEGER DEFAULT NULL REFERENCES tags (tag),
  CONSTRAINT unique_tag_per_parent UNIQUE NULLS NOT DISTINCT (tag_name, parent_tag)
);

CREATE OR REPLACE FUNCTION check_tag_nesting_limit()
RETURNS TRIGGER AS $$
BEGIN
  -- Cannot be own parent
  IF NEW.parent_tag = NEW.tag THEN
    RAISE EXCEPTION 'A tag cannot be its own parent.' USING ERRCODE = 'check_violation';
  END IF;
  IF NEW.parent_tag IS NOT NULL THEN
    -- Child cannot become parent
    IF EXISTS (SELECT 1
               FROM tags
               WHERE tag = NEW.parent_tag
                 AND parent_tag IS NOT NULL
    ) THEN
      RAISE EXCEPTION 'Invalid Nesting: Tag % is already a child. You cannot nest further.', NEW.parent_tag USING ERRCODE = 'integrity_constraint_violation';
    END IF;
    -- Tag with children cannot change into a child
    IF EXISTS (SELECT 1
               FROM tags
               WHERE parent_tag = NEW.tag
    ) THEN
      RAISE EXCEPTION 'Invalid Nesting: Tag % is already a parent. It cannot be nested under another tag.', NEW.tag USING ERRCODE = 'integrity_constraint_violation';
    END IF;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_tag_nesting
BEFORE INSERT OR UPDATE ON tags
FOR EACH ROW
EXECUTE FUNCTION check_tag_nesting_limit();


CREATE TABLE IF NOT EXISTS deltas (
  id_d SERIAL PRIMARY KEY,
  subtitle TEXT,
  ts_log TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  ts TIMESTAMPTZ NOT NULL,
  amount NUMERIC(10, 2) NOT NULL,
  id_a INTEGER NOT NULL REFERENCES accounts (id_a),
  tag INTEGER REFERENCES tags (tag)
);


CREATE TABLE IF NOT EXISTS deltasPerTransaction (
  id_t INTEGER NOT NULL REFERENCES transactions (id_t),
  id_d INTEGER NOT NULL REFERENCES deltas (id_d),
  PRIMARY KEY (id_t, id_d)
);


CREATE VIEW deltasWithBalance AS
SELECT
  d.id_d,
  d.subtitle,
  d.ts_log,
  d.ts,
  d.amount,
  d.id_a,
  d.tag,
  (a.opening_balance + SUM(d.amount) OVER (PARTITION BY d.id_a
                                             ORDER BY d.ts ASC, d.id_d ASC)
  ) AS balance_after
FROM deltas d
JOIN accounts a ON d.id_a = a.id_a;


CREATE VIEW completeDeltaInfo AS
SELECT t.id_t,
       t.title,
       t.pinned,
       d.subtitle,
       tags.tag_name,
       d.id_d,
       d.amount,
       a.currency,
       a.account,
       d.ts,
       d.ts_log,
       d.balance_after
FROM transactions t
JOIN deltasPerTransaction dt ON dt.id_t = t.id_t
JOIN deltasWithBalance d ON d.id_d = dt.id_d
JOIN accounts a ON a.id_a = d.id_a
LEFT JOIN tags ON tags.tag = d.tag;
