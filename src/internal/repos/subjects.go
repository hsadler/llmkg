package repos

import (
	"context"
	"fmt"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
	"github.com/pkg/errors"
	"github.com/rs/zerolog/log"

	"example-server/internal/logger"
	"example-server/internal/models"
)

var (
	RelationshipRelatedTo = "RELATED_TO"

	ErrorCreateSubject         = errors.New("Error creating Subject")
	ErrorSubjectExists         = errors.New("Subject already exists")
	ErrorSubjectNotFound       = errors.New("Subject not found")
	ErrorSubjectQuery          = errors.New("Error querying Subject")
	ErrorCreateSubjectRelation = errors.New("Error creating Subject Relation")
	ErrorSubjectRelationExists = errors.New("Subject Relation already exists")
	ErrorSubjectRelationQuery  = errors.New("Error querying Subject Relation")
)

func TruncateNeo4j(driver neo4j.DriverWithContext) error {
	session := driver.NewSession(context.Background(), neo4j.SessionConfig{
		AccessMode: neo4j.AccessModeWrite,
	})
	defer session.Close(context.Background())
	// Truncate all nodes
	query := "MATCH (n) DETACH DELETE n"
	_, err := session.Run(context.Background(), query, nil)
	if err != nil {
		logger.LogErrorWithStacktrace(err, "Error truncating Neo4j nodes")
		return err
	}
	// Truncate all relationships
	query = "MATCH ()-[r]-() DELETE r"
	_, err = session.Run(context.Background(), query, nil)
	if err != nil {
		logger.LogErrorWithStacktrace(err, "Error truncating Neo4j relationships")
		return err
	}
	return nil
}

// Subject

func CreateSubjectNode(
	driver neo4j.DriverWithContext,
	kgVersion string,
	subjectName string,
) (*models.Subject, error) {
	// Open a session (read/write or read-only)
	session := driver.NewSession(context.Background(), neo4j.SessionConfig{
		AccessMode: neo4j.AccessModeWrite,
	})
	defer session.Close(context.Background())
	// Create Subject Node
	query := fmt.Sprintf(
		"MERGE (n:Subject {name: '%s', kgVersion: '%s'}) RETURN n",
		subjectName,
		kgVersion,
	)
	result, err := session.Run(context.Background(), query, nil)
	if err != nil {
		logger.LogErrorWithStacktrace(err, "Error creating Subject Node")
		return nil, err
	}
	// Move to the next record
	if !result.Next(context.Background()) {
		// Check for errors
		if err = result.Err(); err != nil {
			logger.LogErrorWithStacktrace(err, "Error reading result")
			return nil, err
		}
		return nil, errors.New("No record returned")
	}
	// Get the record
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

func GetSubjectByName(
	driver neo4j.DriverWithContext,
	kgVersion string,
	subjectName string,
) (*models.Subject, error) {
	session := driver.NewSession(context.Background(), neo4j.SessionConfig{
		AccessMode: neo4j.AccessModeRead,
	})
	defer session.Close(context.Background())
	// Get Subject by Name
	query := fmt.Sprintf(
		"MATCH (n:Subject {name: '%s', kgVersion: '%s'}) RETURN n",
		subjectName,
		kgVersion,
	)
	result, err := session.Run(context.Background(), query, nil)
	if err != nil {
		logger.LogErrorWithStacktrace(err, "Error getting Subject by Name")
		return nil, err
	}
	// Move to the next record
	if !result.Next(context.Background()) {
		// Check for errors
		if err = result.Err(); err != nil {
			logger.LogErrorWithStacktrace(err, "Error reading result")
			return nil, err
		}
		return nil, errors.New("No record returned")
	}
	// Get the record
	record := result.Record()
	if record == nil {
		return nil, errors.New("No record returned")
	}
	log.Debug().Interface("record", record).Msg("Subject found")
	// Convert Neo4j record to models.Subject
	subject, err := recordToSubject(record)
	if err != nil {
		logger.LogErrorWithStacktrace(err, "Error converting record to Subject")
		return nil, err
	}
	return subject, nil
}

func CreateSubjectRelation(
	driver neo4j.DriverWithContext,
	kgVersion string,
	subjectID string,
	relatedSubjectID string,
) (*models.SubjectRelation, error) {
	session := driver.NewSession(context.Background(), neo4j.SessionConfig{
		AccessMode: neo4j.AccessModeWrite,
	})
	defer session.Close(context.Background())
	// Create Subject Relation
	query := fmt.Sprintf(`
		MATCH (s:Subject), (r:Subject) 
		WHERE elementId(s) = '%s'
		AND elementId(r) = '%s' AND s.kgVersion = '%s' AND r.kgVersion = '%s'
		MERGE (s)-[:%s]->(r) 
		RETURN s, r`,
		subjectID,
		relatedSubjectID,
		kgVersion,
		kgVersion,
		RelationshipRelatedTo,
	)
	result, err := session.Run(context.Background(), query, nil)
	if err != nil {
		logger.LogErrorWithStacktrace(err, "Error creating Subject Relation")
		return nil, err
	}
	// Move to the next record
	if !result.Next(context.Background()) {
		// Check for errors
		if err = result.Err(); err != nil {
			logger.LogErrorWithStacktrace(err, "Error reading result")
			return nil, err
		}
		return nil, errors.New("No record returned")
	}
	// Get the record
	record := result.Record()
	if record == nil {
		return nil, errors.New("No record returned")
	}
	log.Debug().Interface("record", record).Msg("Subject relation created")
	subjectRelation, err := recordToSubjectRelation(record)
	if err != nil {
		logger.LogErrorWithStacktrace(err, "Error converting record to Subject Relation")
		return nil, err
	}
	return subjectRelation, nil
}

// Helpers

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
	// Get kgVersion
	kgVersionValue, kgVersionExists := properties["kgVersion"]
	if !kgVersionExists {
		return nil, errors.New("kgVersion property not found")
	}
	kgVersion, ok := kgVersionValue.(string)
	if !ok {
		return nil, errors.New("kgVersion is not a string")
	}
	// Convert Neo4j Node to models.Subject
	return &models.Subject{
		ID:        node.ElementId,
		Name:      name,
		KgVersion: kgVersion,
	}, nil
}

func recordToSubjectRelation(record *neo4j.Record) (*models.SubjectRelation, error) {
	// Get the node from the record (assuming it's returned as 'n')
	subj, found := record.Get("s")
	if !found {
		return nil, errors.New("Subject 's' not found in record")
	}
	subjNode, ok := subj.(neo4j.Node)
	if !ok {
		return nil, errors.New("Value is not a Neo4j Node")
	}
	relatedSubj, found := record.Get("r")
	if !found {
		return nil, errors.New("Related subject 'r' not found in record")
	}
	relatedSubjNode, ok := relatedSubj.(neo4j.Node)
	if !ok {
		return nil, errors.New("Value is not a Neo4j Node")
	}
	// Instantiate models.SubjectRelation
	subjectRelation := &models.SubjectRelation{
		SubjectID:        subjNode.ElementId,
		RelatedSubjectID: relatedSubjNode.ElementId,
	}
	return subjectRelation, nil
}
