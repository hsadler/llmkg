package repos

import (
	"context"
	"fmt"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
	"github.com/pkg/errors"
	"github.com/rs/zerolog/log"

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

func TruncateTables(dbPool database.PgxPoolIface) error {
	_, err := dbPool.Exec(context.Background(), "TRUNCATE TABLE subject")
	if err != nil {
		logger.LogErrorWithStacktrace(err, "Error truncating subject table")
		return err
	}
	_, err = dbPool.Exec(context.Background(), "TRUNCATE TABLE subject_relation")
	if err != nil {
		logger.LogErrorWithStacktrace(err, "Error truncating subject_relation table")
		return err
	}
	return nil
}

// Subject

func CreateSubjectNode(driver neo4j.DriverWithContext, subjectName string) (*models.Subject, error) {
	// Open a session (read/write or read-only)
	session := driver.NewSession(context.Background(), neo4j.SessionConfig{
		AccessMode: neo4j.AccessModeWrite,
	})
	defer session.Close(context.Background())
	// Create Subject Node
	query := fmt.Sprintf(
		"CREATE (n:Subject {name: '%s'}) RETURN n",
		subjectName,
	)
	result, err := session.Run(context.Background(), query, nil)
	if err != nil {
		logger.LogErrorWithStacktrace(err, "Error creating Subject Node")
		return nil, err
	}
	if !result.Next(context.Background()) {
		// Check for errors
		if err = result.Err(); err != nil {
			logger.LogErrorWithStacktrace(err, "Error reading result")
			return nil, err
		}
		return nil, errors.New("No record returned")
	}
	record := result.Record()
	if record == nil {
		return nil, errors.New("No record returned")
	}
	log.Debug().Interface("record", record).Msg("Subject created")
	// Convert Neo4j record to models.Subject
	subject, err := recordToSubject(record)
	if err != nil {
		logger.LogErrorWithStacktrace(err, "Error converting record to Subject")
		return nil, err
	}
	return subject, nil
}

func recordToSubject(record *neo4j.Record) (*models.Subject, error) {
	// Get the node from the record (assuming it's returned as 'n')
	nodeValue, found := record.Get("n")
	if !found {
		return nil, errors.New("Node 'n' not found in record")
	}
	// Cast to Neo4j Node
	node, ok := nodeValue.(neo4j.Node)
	if !ok {
		return nil, errors.New("Value is not a Neo4j Node")
	}
	// Extract properties
	properties := node.Props
	// Get name
	nameValue, nameExists := properties["name"]
	if !nameExists {
		return nil, errors.New("Name property not found")
	}
	name, ok := nameValue.(string)
	if !ok {
		return nil, errors.New("Name is not a string")
	}
	// Convert Neo4j Node to models.Subject
	return &models.Subject{
		ID:   node.ElementId,
		Name: name,
	}, nil
}
