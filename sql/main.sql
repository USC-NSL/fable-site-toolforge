PRAGMA foreign_keys = ON;

CREATE TABLE aliases(
    id varchar(500),
    alias VARCHAR(2048) NOT NULL,
    link VARCHAR(2048) NOT NULL,
    article VARCHAR(2048) NOT NULL,
    PRIMARY KEY(id)
);

CREATE TABLE feedback(
    accurate INTEGER,
    inaccurate INTEGER,
    mid INTEGER,
    alias_id varchar(500),
    PRIMARY KEY(alias_id)
    CONSTRAINT FK_alias FOREIGN KEY (alias_id) 
    REFERENCES alias(id)
    ON DELETE CASCADE
);

CREATE TABLE id(
    accurate INTEGER,
    inaccurate INTEGER,
    mid INTEGER,
    user VARCHAR(2048),
    feedback TEXT, 
    alias_id varchar(500),
    CONSTRAINT FK_alias FOREIGN KEY (alias_id) 
    REFERENCES alias(id)
    ON DELETE CASCADE
);


