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
	ErrorCreateItem   = errors.New("Error creating Item")
	ErrorItemsQuery   = errors.New("Error querying Items")
	ErrorUpdateItem   = errors.New("Error updating Item")
	ErrorDeleteItem   = errors.New("Error deleting Item")
	ErrorItemNotFound = errors.New("Item not found")
	ErrorItemExists   = errors.New("Item already exists")
)

func InsertItem(dbPool database.PgxPoolIface, itemIn models.ItemIn) (*models.Item, error) {
	// Insert Item
	var itemId int
	err := dbPool.QueryRow(
		context.Background(),
		"INSERT INTO item (name, price) VALUES ($1, $2) RETURNING id",
		itemIn.Name,
		itemIn.Price,
	).Scan(&itemId)
	// Handle Item insert error
	if err != nil {
		var pgErr *pgconn.PgError
		if errors.As(err, &pgErr) {
			// Duplicate entry error handling
			if pgErr.Code == "23505" {
				return nil, ErrorItemExists
			}
		}
		logger.LogErrorWithStacktrace(err, "Error inserting Item")
		return nil, ErrorCreateItem
	}
	// Fetch Item by ID
	item, err := FetchItemById(dbPool, itemId)
	if err != nil {
		return nil, err
	}
	return item, nil
}

func FetchItemById(dbPool database.PgxPoolIface, itemId int) (*models.Item, error) {
	// Fetch Item by ID
	var item models.Item
	err := dbPool.QueryRow(
		context.Background(),
		"SELECT id, uuid, created_at, name, price FROM item WHERE id = $1",
		itemId,
	).Scan(&item.ID, &item.UUID, &item.CreatedAt, &item.Name, &item.Price)
	// Handle Item fetch error
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return nil, ErrorItemNotFound
		}
		logger.LogErrorWithStacktrace(err, "Error querying Item")
		return nil, ErrorItemsQuery
	}
	return &item, nil
}

func UpdateItem(
	dbPool database.PgxPoolIface,
	itemId int,
	itemIn models.ItemIn,
) (*models.Item, error) {
	// Update Item
	var item models.Item
	err := dbPool.QueryRow(
		context.Background(),
		"UPDATE item SET name = $1, price = $2 WHERE id = $3 RETURNING id, uuid, created_at, name, price",
		itemIn.Name,
		itemIn.Price,
		itemId,
	).Scan(&item.ID, &item.UUID, &item.CreatedAt, &item.Name, &item.Price)
	// Handle Item update error
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return nil, ErrorItemNotFound
		}
		var pgErr *pgconn.PgError
		if errors.As(err, &pgErr) {
			// Duplicate entry error handling
			if pgErr.Code == "23505" {
				return nil, ErrorItemExists
			}
		}
		logger.LogErrorWithStacktrace(err, "Error updating Item")
		return nil, ErrorUpdateItem
	}
	return &item, nil
}

func DeleteItem(
	dbPool database.PgxPoolIface,
	itemId int,
) (*models.Item, error) {
	// Fetch Item by ID
	item, fetchErr := FetchItemById(dbPool, itemId)
	if fetchErr != nil {
		return nil, fetchErr
	}
	if item == nil {
		return nil, ErrorItemNotFound
	}
	// Delete Item if it exists
	_, deleteErr := dbPool.Exec(
		context.Background(),
		"DELETE FROM item WHERE id = $1",
		itemId,
	)
	// Handle Item delete error
	if deleteErr != nil {
		logger.LogErrorWithStacktrace(deleteErr, "Error deleting Item")
		return nil, ErrorDeleteItem
	}
	return item, nil
}
