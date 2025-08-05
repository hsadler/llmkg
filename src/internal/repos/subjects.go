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
	ErrorSubjectRelationQuery  = errors.New("Error querying Subject Relation")
)

// Subject

func InsertSubject(dbPool database.PgxPoolIface, subjectIn models.SubjectIn) (*models.Subject, error) {
	// Insert Subject
	var subject models.Subject
	err := dbPool.QueryRow(
		context.Background(),
		"INSERT INTO subject (name) VALUES ($1) RETURNING id, uuid, created_at, name",
		subjectIn.Name,
	).Scan(&subject.ID, &subject.UUID, &subject.CreatedAt, &subject.Name)
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
	return &subject, nil
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

func FetchSubjectRelationsBySubjectId(
	dbPool database.PgxPoolIface,
	subjectId int,
) ([]models.SubjectRelation, error) {
	// Fetch Subject Relations rows by Subject ID
	var subjectRelations []models.SubjectRelation
	rows, err := dbPool.Query(
		context.Background(),
		"SELECT id, created_at, subject_id, related_subject_id FROM subject_relation WHERE subject_id = $1",
		subjectId,
	)
	if err != nil {
		logger.LogErrorWithStacktrace(err, "Error querying Subject Relation")
		return nil, err
	}
	defer rows.Close()
	// Scan rows into subjectRelations
	for rows.Next() {
		var subjectRelation models.SubjectRelation
		err := rows.Scan(
			&subjectRelation.ID,
			&subjectRelation.CreatedAt,
			&subjectRelation.SubjectID,
			&subjectRelation.RelatedSubjectID,
		)
		if err != nil {
			logger.LogErrorWithStacktrace(err, "Error scanning Subject Relation")
			return nil, ErrorSubjectRelationQuery
		}
		subjectRelations = append(subjectRelations, subjectRelation)
	}
	return subjectRelations, nil
}

func FetchSubjectRelationsByRelatedSubjectId(
	dbPool database.PgxPoolIface,
	relatedSubjectId int,
) ([]models.SubjectRelation, error) {
	// Fetch Subject Relations rows by Related Subject ID
	var subjectRelations []models.SubjectRelation
	rows, err := dbPool.Query(
		context.Background(),
		"SELECT id, created_at, subject_id, related_subject_id FROM subject_relation WHERE related_subject_id = $1",
		relatedSubjectId,
	)
	if err != nil {
		logger.LogErrorWithStacktrace(err, "Error querying Subject Relation")
		return nil, err
	}
	defer rows.Close()
	// Scan rows into subjectRelations
	for rows.Next() {
		var subjectRelation models.SubjectRelation
		err := rows.Scan(
			&subjectRelation.ID,
			&subjectRelation.CreatedAt,
			&subjectRelation.SubjectID,
			&subjectRelation.RelatedSubjectID,
		)
		if err != nil {
			logger.LogErrorWithStacktrace(err, "Error scanning Subject Relation")
			return nil, ErrorSubjectRelationQuery
		}
		subjectRelations = append(subjectRelations, subjectRelation)
	}
	return subjectRelations, nil
}
