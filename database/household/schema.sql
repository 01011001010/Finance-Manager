-- TODO enriched views:
-- roll up weight/volume, ...
-- density
-- display names


-- TODO tables:
-- log
-- notes

-- TODO
-- use _raw for base tables, and plain for enriched views


CREATE EXTENSION IF NOT EXISTS CITEXT;

CREATE TYPE allowedUnit AS ENUM ('ml', 'l', 'g', 'kg', 'm', 'cm', 'mm');
CREATE TYPE allowedTimeUnit AS ENUM ('D', 'M', 'Y');
CREATE TYPE location AS ENUM ('storage', 'refrigerator', 'freezer');

CREATE SCHEMA stock;


CREATE TABLE IF NOT EXISTS stock.stores (
  id_s SERIAL PRIMARY KEY,
  name CITEXT NOT NULL,
  country CHAR(3) NOT NULL,
  currency CHAR(3) NOT NULL,
  archived BOOLEAN NOT NULL DEFAULT FALSE,
  CONSTRAINT unique_account_details UNIQUE (name, country)
);


CREATE TABLE IF NOT EXISTS stock.categories (
  id_c SERIAL PRIMARY KEY,
  name CITEXT NOT NULL UNIQUE
);


CREATE TABLE IF NOT EXISTS stock.units (
  id_u SERIAL PRIMARY KEY,
  weight_net_g NUMERIC(6,1),
  weight_tare_g NUMERIC(6,1),
  volume_ml NUMERIC(6,1),
  length_m NUMERIC(7,1),
  display_unit_weight allowedUnit NOT NULL DEFAULT 'kg',
  display_unit_volume allowedUnit NOT NULL DEFAULT 'l',
  display_unit_length allowedUnit NOT NULL DEFAULT 'm',
  open_date DATE DEFAULT NULL,
  finish_date DATE DEFAULT NULL,
  CONSTRAINT at_least_one_amount
        CHECK (weight_net_g IS NOT NULL OR volume_ml IS NOT NULL OR length_m IS NOT NULL)
);


CREATE TABLE IF NOT EXISTS stock.packages (
  id_p SERIAL PRIMARY KEY,
  expiration_date DATE DEFAULT NULL,
  toss_after_opening_value smallint DEFAULT NULL,
  toss_after_opening_unit allowedTimeUnit DEFAULT 'M',
);


CREATE TABLE IF NOT EXISTS stock.lots (
  id_l SERIAL PRIMARY KEY,
  id_s INTEGER NOT NULL REFERENCES stock.stores (id_s),
  id_c INTEGER NOT NULL REFERENCES stock.stores (id_c),
  bought_date DATE NOT NULL,
  price NUMERIC(7, 2) NOT NULL,
  item_type TEXT DEFAULT NULL,
  name TEXT NOT NULL,
  variant TEXT DEFAULT NULL,
  brand TEXT DEFAULT NULL,
  current_location location NOT NULL DEFAULT 'storage'
);


CREATE TABLE IF NOT EXISTS stock.unitsPerPackages (
  id_u INTEGER NOT NULL REFERENCES stock.units (id_u) UNIQUE,
  id_p INTEGER NOT NULL REFERENCES stock.packages (id_p),
  PRIMARY KEY (id_u, id_p)
);


CREATE TABLE IF NOT EXISTS stock.packagesPerLots (
  id_p INTEGER NOT NULL REFERENCES stock.packages (id_p) UNIQUE,
  id_l INTEGER NOT NULL REFERENCES stock.lots (id_l),
  PRIMARY KEY (id_p, id_l)
);
