CREATE TABLE tweets(
	id BIGINT PRIMARY KEY NOT NULL,
	created_at TIMESTAMP NOT NULL,
	tweet_text TEXT
	);

CREATE TABLE station_pulls(
    id BIGINT PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    lines TEXT[],
    has_machines BOOLEAN,
    is_accessible BOOLEAN,
    elevator_count_words TEXT,
    escalator_count_words TEXT,
    outages TEXT,
    accessible_note TEXT,
    pull_time TIMESTAMP
);
