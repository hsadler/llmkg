CREATE TABLE subject_relation (
    id SERIAL PRIMARY KEY,
    subject_id INT NOT NULL,
    related_subject_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT subject_relation_subject_id_related_subject_id_unique UNIQUE (subject_id, related_subject_id)
);