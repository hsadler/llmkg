package dependencies

import (
	"example-server/internal/database"
)

type Dependencies struct {
	DBPool database.PgxPoolIface
}

func NewDependencies(
	pgxPool database.PgxPoolIface,
) *Dependencies {
	return &Dependencies{
		DBPool: pgxPool,
	}
}

func (deps *Dependencies) CleanupDependencies() {
	deps.DBPool.Close()
}
