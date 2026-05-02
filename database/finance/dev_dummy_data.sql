INSERT INTO finance.accounts (account, currency)
VALUES
  ('Cash', 'EUR'),
  ('Cash', 'CHF'),
  ('Online bank', 'GBP'),
  ('Online bank', 'CHF'),
  ('Bank', 'CHF'),
  ('Bank', 'EUR');


INSERT INTO finance.transactions (title)
VALUES
  ('Christmas'),
  ('Supermarket'),
  ('Boutique'),
  ('Rent'),
  ('Opening balance');


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
  (NULL, -7.42, 6, 2, '2026-01-06 16:16:42+01'),
  (NULL,50,1,NULL,'2000-01-01 05:00:00+01'),
  (NULL,200,2,NULL,'2000-01-01 05:00:00+01'),
  (NULL,50,3,NULL,'2000-01-01 05:00:00+01'),
  (NULL,1000,4,NULL,'2000-01-01 05:00:00+01'),
  (NULL,700,5,NULL,'2000-01-01 05:00:00+01'),
  (NULL,800,6,NULL,'2000-01-01 05:00:00+01');


INSERT INTO finance.deltasPerTransaction (id_t, id_d)
VALUES
  (1, 1),
  (1, 2),
  (2, 3),
  (2, 4),
  (3, 5),
  (4, 6),
  (4, 7),
  (2, 8),
  (5, 9),
  (5, 10),
  (5, 11),
  (5, 12),
  (5, 13),
  (5, 14);
