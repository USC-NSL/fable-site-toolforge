create schema s55570__fable;

use s55570__fable;

CREATE TABLE aliases (
  id INT NOT NULL AUTO_INCREMENT,
  article TEXT,
  link TEXT,
  alias TEXT,
  feedbackSelection TEXT,
  feedbackInput TEXT,
  PRIMARY KEY (id)
)

ALTER TABLE aliases
ADD COLUMN lastModifiedBy VARCHAR(255);