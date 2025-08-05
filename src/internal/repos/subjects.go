package repos

import (
	"context"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgconn"
	"github.com/pkg/errors"

	"example-server/internal/database"
	"example-server/internal/logger"
	"example-server/internal/models"
)

var (
	ErrorCreateSubject         = errors.New("Error creating Subject")
	ErrorSubjectExists         = errors.New("Subject already exists")
	ErrorSubjectNotFound       = errors.New("Subject not found")
	ErrorSubjectQuery          = errors.New("Error querying Subject")
	ErrorCreateSubjectRelation = errors.New("Error creating Subject Relation")
	ErrorSubjectRelationExists = errors.New("Subject Relation already exists")
)

// Subject

func InsertSubject(dbPool database.PgxPoolIface, subjectIn models.SubjectIn) (*models.Subject, error) {
	// Insert Subject
	var subjectId int
	err := dbPool.QueryRow(
		context.Background(),
		"INSERT INTO subject (name) VALUES ($1) RETURNING id",
		subjectIn.Name,
	).Scan(&subjectId)
	// Handle Subject insert error
	if err != nil {
		var pgErr *pgconn.PgError
		if errors.As(err, &pgErr) {
			// Duplicate entry error handling
			if pgErr.Code == "23505" {
				return nil, ErrorSubjectExists
			}
		}
		logger.LogErrorWithStacktrace(err, "Error inserting Subject")
		return nil, ErrorCreateSubject
	}
	// Fetch Subject by ID
	subject, err := FetchSubjectById(dbPool, subjectId)
	if err != nil {
		return nil, err
	}
	return subject, nil
}

func FetchSubjectById(dbPool database.PgxPoolIface, subjectId int) (*models.Subject, error) {
	// Fetch Subject by ID
	var subject models.Subject
	err := dbPool.QueryRow(
		context.Background(),
		"SELECT id, uuid, created_at, name FROM subject WHERE id = $1",
		subjectId,
	).Scan(&subject.ID, &subject.UUID, &subject.CreatedAt, &subject.Name)
	// Handle Subject fetch error
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return nil, ErrorSubjectNotFound
		}
		logger.LogErrorWithStacktrace(err, "Error querying Subject")
		return nil, ErrorSubjectQuery
	}
	return &subject, nil
}

// Subject Relation

func InsertSubjectRelation(
	dbPool database.PgxPoolIface,
	subjectRelationIn models.SubjectRelationIn,
) (*models.SubjectRelation, error) {
	// Insert Subject Relation
	var subjectRelation models.SubjectRelation
	err := dbPool.QueryRow(
		context.Background(),
		`INSERT INTO subject_relation (subject_id, related_subject_id) 
		VALUES ($1, $2) 
		RETURNING id, created_at, subject_id, related_subject_id`,
		subjectRelationIn.SubjectID, subjectRelationIn.RelatedSubjectID,
	).Scan(
		&subjectRelation.ID,
		&subjectRelation.CreatedAt,
		&subjectRelation.SubjectID,
		&subjectRelation.RelatedSubjectID,
	)
	// Handle Subject Relation insert error
	if err != nil {
		var pgErr *pgconn.PgError
		if errors.As(err, &pgErr) {
			// Duplicate entry error handling
			if pgErr.Code == "23505" {
				return nil, ErrorSubjectRelationExists
			}
		}
		logger.LogErrorWithStacktrace(err, "Error inserting Subject Relation")
		return nil, ErrorCreateSubjectRelation
	}
	return &subjectRelation, nil
}
