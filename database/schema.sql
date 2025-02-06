-- This file should contain all code required to create & seed database tables.

DROP TABLE IF EXISTS rating_interaction CASCADE;
DROP TABLE IF EXISTS request_interaction CASCADE;
DROP TABLE IF EXISTS exhibition CASCADE;
DROP TABLE IF EXISTS rating;
DROP TABLE IF EXISTS request;
DROP TABLE IF EXISTS floor;
DROP TABLE IF EXISTS department;


CREATE TABLE department(
    department_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    department_name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE floor(
    floor_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    floor_name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE request(
    request_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    request_value SMALLINT UNIQUE NOT NULL CHECK (request_value = 0 OR request_value = 1), 
    request_description VARCHAR(100),
    CONSTRAINT valid_match_request CHECK ( 
        (request_value = 0 AND request_description ILIKE 'assistance') 
        OR (request_value = 1 AND request_description ILIKE 'emergency'))
);

CREATE TABLE rating(
    rating_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rating_value SMALLINT UNIQUE NOT NULL CHECK (rating_value >= 0 AND rating_value <= 4),
    rating_description VARCHAR(100),
    CONSTRAINT valid_match_rating CHECK ( 
        (rating_value = 0 AND rating_description ILIKE 'terrible')
        OR (rating_value = 1 AND rating_description ILIKE 'bad')
        OR (rating_value = 2 AND rating_description ILIKE 'neutral')
        OR (rating_value = 3 AND rating_description ILIKE 'good')
        OR (rating_value = 4 AND rating_description ILIKE 'amazing'))
);

CREATE TABLE exhibition(
    exhibition_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    exhibition_name VARCHAR(100) UNIQUE NOT NULL,
    exhibition_description TEXT UNIQUE NOT NULL,
    exhibition_start_date DATE NOT NULL,
    public_id VARCHAR(100) NOT NULL,
    department_id SMALLINT NOT NULL,
    floor_id SMALLINT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES department(department_id) ON DELETE CASCADE,
    FOREIGN KEY (floor_id) REFERENCES floor(floor_id) ON DELETE CASCADE
);

CREATE TABLE request_interaction(
    request_interaction_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exhibition_id SMALLINT NOT NULL,
    request_id SMALLINT NOT NULL,
    FOREIGN KEY (exhibition_id) REFERENCES exhibition(exhibition_id) ON DELETE CASCADE,
    FOREIGN KEY (request_id) REFERENCES request(request_id) ON DELETE CASCADE
);

CREATE TABLE rating_interaction(
    rating_interaction_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exhibition_id SMALLINT NOT NULL,
    rating_id SMALLINT NOT NULL,
    FOREIGN KEY (exhibition_id) REFERENCES exhibition(exhibition_id) ON DELETE CASCADE,
    FOREIGN KEY (rating_id) REFERENCES rating(rating_id) ON DELETE CASCADE
);

CREATE INDEX rating_interaction_idx ON rating_interaction(exhibition_id, rating_id);
CREATE INDEX request_interaction_idx ON request_interaction(exhibition_id, request_id);
CREATE INDEX exhibition_idx ON exhibition(department_id, floor_id);

INSERT INTO request (request_value, request_description) VALUES
(0, 'assistance'), 
(1, 'emergency');

INSERT INTO rating (rating_value, rating_description) VALUES
(0, 'Terrible'),
(1, 'Bad'),
(2, 'Neutral'),
(3, 'Good'),
(4, 'Amazing');

INSERT INTO floor (floor_name) VALUES
('vault'),
('1'),
('2'),
('3');

INSERT INTO department (department_name) VALUES
('Entomology'),
('Geology'),
('Paleontology'),
('Zoology'),
('Ecology');

INSERT INTO exhibition (public_id, exhibition_name, exhibition_start_date, exhibition_description, floor_id, department_id) VALUES
('EXH_00', 'Measureless to Man', '08/23/2021', 'An immersive 3D experience: delve deep into a previously-inaccessible cave system.', 2, 2),
('EXH_01', 'Adaptation', '07/01/2019', 'How insect evolution has kept pace with an industrialised world.', 1, 1),
('EXH_02', 'The Crenshaw Collection', '03/03/2021', 'An exhibition of 18th Century watercolours, mostly focused on South American wildlife.', 4, 4),
('EXH_03', 'Cetacean Sensations', '07/01/2019', 'Whales: from ancient myth to critically endangered.', 2, 4),
('EXH_04', 'Our Polluted World', '05/12/2021', 'A hard-hitting exploration of humanity''s impact on the environment.', 4, 5),
('EXH_05', 'Thunder Lizards', '02/01/2023', 'How new research is making scientists rethink what dinosaurs really looked like.', 2, 3);

