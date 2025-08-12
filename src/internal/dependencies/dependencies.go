package dependencies

import (
	"context"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

type Dependencies struct {
	Neo4jDriver neo4j.DriverWithContext
}

func NewDependencies(
	neo4jDriver neo4j.DriverWithContext,
) *Dependencies {
	return &Dependencies{
		Neo4jDriver: neo4jDriver,
	}
}

func (deps *Dependencies) CleanupDependencies() {
	deps.Neo4jDriver.Close(context.Background())
}
