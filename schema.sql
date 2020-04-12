CREATE TYPE tabsite AS ENUM ('Tabbycat', 'MIT-Tab');

CREATE TABLE IF NOT EXISTS tournament (
	id SERIAL PRIMARY KEY,
	url VARCHAR(150) NULL,
	tabsite_type tabsite NULL,
	guild_id BIGINT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS team (
	id SERIAL PRIMARY KEY,
	tournament INT NOT NULL REFERENCES tournament(id) ON DELETE CASCADE,
	tab_id INT NOT NULL,
	CONSTRAINT tournament_tab_uniq UNIQUE (tournament, tab_id)
);

CREATE TABLE IF NOT EXISTS speaker (
	id SERIAL PRIMARY KEY,
	team       INT NOT NULL REFERENCES team(id)       ON DELETE CASCADE,
	discord_name VARCHAR(35) NULL,
	tab_id INT NOT NULL
);

CREATE TABLE IF NOT EXISTS adjudicator (
	id SERIAL PRIMARY KEY,
	tournament INT NOT NULL REFERENCES tournament(id) ON DELETE CASCADE,
	discord_name VARCHAR(35) NULL,
	tab_id INT NOT NULL,
	CONSTRAINT adjudicator_tab_uniq UNIQUE (tournament, tab_id)
);

CREATE TABLE IF NOT EXISTS room (
	id SERIAL PRIMARY KEY,
	tournament INT NOT NULL REFERENCES tournament(id) ON DELETE CASCADE,
	channel BIGINT NULL,
	tab_id INT NOT NULL
);
