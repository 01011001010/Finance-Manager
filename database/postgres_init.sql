CREATE TABLE IF NOT EXISTS accounts (
    id_a SERIAL PRIMARY KEY,
    account TEXT NOT NULL,
    currency CHAR(3) NOT NULL
);
INSERT INTO accounts (account, currency)
VALUES
  ('Cash', 'EUR'),
  ('Cash', 'CHF'),
  ('Online bank', 'GBP'),
  ('Online bank', 'CHF'),
  ('Bank', 'CHF'),
  ('Bank', 'EUR');



CREATE TABLE IF NOT EXISTS transactions (
    id_t SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    subtitle TEXT
);
INSERT INTO transactions (title, subtitle)
VALUES
  ('Christmas', 'Parents'),
  ('Christmas', 'Grandparents'),
  ('Supermarket', NULL),
  ('Boutique',  NULL),
  ('January rent', NULL);



CREATE TABLE IF NOT EXISTS tags (
    tag SERIAL PRIMARY KEY,
    tag_name TEXT NOT NULL
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
    ts_log TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ts TIMESTAMPTZ NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    id_a INTEGER NOT NULL REFERENCES accounts (id_a),
    tag INTEGER REFERENCES tags (tag)
);
INSERT INTO deltas (amount, id_a, tag, ts)
VALUES
  (10, 6, 1, '2025-12-24 20:00:00+01'),
  (1, 1, 1, '2025-12-24 20:01:00+01'),
  (-20, 6, 2, '2025-12-28 12:00:00+01'),
  (-6.85,  1, 2, '2025-12-28 12:00:00+01'),
  (-57,  4, 3, '2025-12-28 12:30:00+01'),
  (-100,  5, 4, '2026-01-01 09:00:00+01'),
  (-2.85,  5, 5, '2026-01-01 09:00:00+01');



CREATE TABLE IF NOT EXISTS deltasPerTransaction (
    id_t INTEGER NOT NULL REFERENCES transactions (id_t),
    id_d INTEGER NOT NULL REFERENCES deltas (id_d),
    PRIMARY KEY (id_t, id_d)
);
INSERT INTO deltasPerTransaction (id_t, id_d)
VALUES
  (1, 1),
  (2, 2),
  (3, 3),
  (3, 4),
  (4, 5),
  (5, 6),
  (5, 7);
