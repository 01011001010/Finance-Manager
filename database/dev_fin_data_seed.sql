INSERT INTO finance.accounts (account, currency, opening_balance)
VALUES
  ('Cash', 'EUR', 50),
  ('Cash', 'CHF', 150),
  ('Online bank', 'GBP', 50),
  ('Online bank', 'CHF', 500),
  ('Bank', 'CHF', 100),
  ('Bank', 'EUR', 200);


INSERT INTO finance.transactions (title)
VALUES
  ('Christmas'),
  ('Supermarket'),
  ('Boutique'),
  ('Rent');


INSERT INTO finance.tags (tag_name, parent_tag)
VALUES
  ('Gift', NULL),
  ('Food', NULL),
  ('Apparel', NULL),
  ('Rent', NULL),
  ('Bank', NULL),
  ('Fees', 5),
  ('Interest', 5);


INSERT INTO finance.deltas (subtitle, amount, id_a, tag, ts)
VALUES
  ('Parents', 10, 6, 1, '2025-12-24 20:00:00+01'),
  ('Grandparents', 1, 1, 1, '2025-12-24 20:01:00+01'),
  (NULL, -20, 1, 2, '2025-12-28 12:00:00+01'),
  (NULL, -6.85,  6, 2, '2025-12-28 12:00:00+01'),
  (NULL, -57,  4, 3, '2025-12-28 12:30:00+01'),
  ('January', -100,  5, 4, '2026-01-01 09:00:00+01'),
  ('January', -2.85,  5, 5, '2026-01-01 09:00:00+01'),
  (NULL, -7.42, 6, 2, '2026-01-06 16:16:42+01');


INSERT INTO finance.deltasPerTransaction (id_t, id_d)
VALUES
  (1, 1),
  (1, 2),
  (2, 3),
  (2, 4),
  (3, 5),
  (4, 6),
  (4, 7),
  (2, 8);
