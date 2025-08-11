package dependencies

import (
	"context"
	"example-server/internal/database"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

type Dependencies struct {
	DBPool      database.PgxPoolIface
	Neo4jDriver neo4j.DriverWithContext
}

func NewDependencies(
	pgxPool database.PgxPoolIface,
	neo4jDriver neo4j.DriverWithContext,
) *Dependencies {
	return &Dependencies{
		DBPool:      pgxPool,
		Neo4jDriver: neo4jDriver,
	}
}

func (deps *Dependencies) CleanupDependencies() {
	deps.DBPool.Close()
	deps.Neo4jDriver.Close(context.Background())
}
