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
INSERT INTO accounts (account, currency, opening_balance)
VALUES
  ('Cash', 'EUR', 50),
  ('Cash', 'CHF', 150),
  ('Online bank', 'GBP', 50),
  ('Online bank', 'CHF', 500),
  ('Bank', 'CHF', 100),
  ('Bank', 'EUR', 200);



CREATE TABLE IF NOT EXISTS transactions (
    id_t SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    pinned BOOLEAN NOT NULL DEFAULT FALSE
);
INSERT INTO transactions (title)
VALUES
  ('Christmas'),
  ('Supermarket'),
  ('Boutique'),
  ('Rent');



CREATE TABLE IF NOT EXISTS tags (
    tag SERIAL PRIMARY KEY,
    tag_name CITEXT UNIQUE NOT NULL,
    archived BOOLEAN NOT NULL DEFAULT FALSE
);
INSERT INTO tags (tag_name)
VALUES
  ('Gift'),
  ('Food'),
  ('Apparel'),
  ('Rent'),
  ('Bank fees');



CREATE TABLE IF NOT EXISTS deltas (
    id_d SERIAL PRIMARY KEY,
    subtitle TEXT,
    ts_log TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ts TIMESTAMPTZ NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    id_a INTEGER NOT NULL REFERENCES accounts (id_a),
    tag INTEGER REFERENCES tags (tag)
);
INSERT INTO deltas (subtitle, amount, id_a, tag, ts)
VALUES
  ('Parents', 10, 6, 1, '2025-12-24 20:00:00+01'),
  ('Grandparents', 1, 1, 1, '2025-12-24 20:01:00+01'),
  (NULL, -20, 1, 2, '2025-12-28 12:00:00+01'),
  (NULL, -6.85,  6, 2, '2025-12-28 12:00:00+01'),
  (NULL, -57,  4, 3, '2025-12-28 12:30:00+01'),
  ('January', -100,  5, 4, '2026-01-01 09:00:00+01'),
  ('January', -2.85,  5, 5, '2026-01-01 09:00:00+01'),
  (NULL, -7.42, 6, 2, '2026-01-06 16:16:42+01');



CREATE TABLE IF NOT EXISTS deltasPerTransaction (
    id_t INTEGER NOT NULL REFERENCES transactions (id_t),
    id_d INTEGER NOT NULL REFERENCES deltas (id_d),
    PRIMARY KEY (id_t, id_d)
);
INSERT INTO deltasPerTransaction (id_t, id_d)
VALUES
  (1, 1),
  (1, 2),
  (2, 3),
  (2, 4),
  (3, 5),
  (4, 6),
  (4, 7),
  (2, 8);


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
