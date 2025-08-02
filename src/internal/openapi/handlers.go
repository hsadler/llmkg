package openapi

import (
	"context"
	"net/http"

	"github.com/google/uuid"
	"github.com/rs/zerolog/log"

	"example-server/internal/dependencies"
	"example-server/internal/models"
	"example-server/internal/openapi/ogen"
	itemsrepo "example-server/internal/repos"
)

type ItemsService struct {
	Deps *dependencies.Dependencies
}

func (s *ItemsService) NewError(ctx context.Context, err error) *ogen.ErrorResponseStatusCode {
	return &ogen.ErrorResponseStatusCode{
		StatusCode: http.StatusInternalServerError,
		Response:   ogen.ErrorResponse{Error: err.Error()},
	}
}

func (s *ItemsService) Ping(
	ctx context.Context,
) (*ogen.PingResponse, error) {
	log.Info().Msg("Handling ping request")
	return &ogen.PingResponse{
		Message: "pong",
	}, nil
}

func (s *ItemsService) CreateItem(
	ctx context.Context,
	req *ogen.ItemCreateRequest,
) (ogen.CreateItemRes, error) {
	log.Info().Interface("ItemCreateRequest", req).Msg("Handling item create request")
	// Insert item
	itemIn := req.Data
	item, err := itemsrepo.InsertItem(s.Deps.DBPool, models.ItemIn{
		Name:  itemIn.Name,
		Price: itemIn.Price,
	})
	if err != nil {
		log.Error().Err(err).Interface("ItemCreateRequest", req).Msg("Error inserting item")
		return nil, s.NewError(ctx, err)
	}
	log.Debug().Interface("item", item).Msg("Item created")
	// Convert models.Item to ogen.Item
	itemOut := ogen.Item{
		ID:        int64(item.ID),
		UUID:      uuid.MustParse(item.UUID),
		CreatedAt: item.CreatedAt,
		Name:      item.Name,
		Price:     item.Price,
	}
	// Compose and return response
	return &ogen.ItemCreateResponse{
		Data: itemOut,
		Meta: ogen.ItemMeta{
			ItemStatus: ogen.OptItemMetaItemStatus{
				Value: ogen.ItemMetaItemStatusCreated,
				Set:   true,
			},
		},
	}, nil
}

func (s *ItemsService) GetItem(
	ctx context.Context,
	params ogen.GetItemParams,
) (ogen.GetItemRes, error) {
	log.Info().Interface("GetItemParams", params).Msg("Handling item get request")
	// Fetch item
	itemId := params.ItemId
	item, err := itemsrepo.FetchItemById(s.Deps.DBPool, itemId)
	if err != nil {
		log.Error().Err(err).Interface("GetItemParams", params).Msg("Error getting item")
		return nil, s.NewError(ctx, err)
	}
	log.Debug().Interface("item", item).Msg("Item fetched")
	// Convert models.Item to ogen.Item
	itemOut := ogen.Item{
		ID:        int64(item.ID),
		UUID:      uuid.MustParse(item.UUID),
		CreatedAt: item.CreatedAt,
		Name:      item.Name,
		Price:     item.Price,
	}
	// Compose and return response
	return &ogen.ItemGetResponse{
		Data: itemOut,
		Meta: ogen.ItemMeta{
			ItemStatus: ogen.OptItemMetaItemStatus{
				Value: ogen.ItemMetaItemStatusFetched,
				Set:   true,
			},
		},
	}, nil
}

func (s *ItemsService) UpdateItem(
	ctx context.Context,
	req *ogen.ItemUpdateRequest,
	params ogen.UpdateItemParams,
) (ogen.UpdateItemRes, error) {
	log.Info().Interface("ItemUpdateRequest", req).Msg("Handling item update request")
	// Update item
	itemId := params.ItemId
	itemIn := req.Data
	item, err := itemsrepo.UpdateItem(s.Deps.DBPool, itemId, models.ItemIn{
		Name:  itemIn.Name,
		Price: itemIn.Price,
	})
	if err != nil {
		log.Error().Err(err).Interface("ItemUpdateRequest", req).Msg("Error updating item")
		return nil, s.NewError(ctx, err)
	}
	log.Debug().Interface("item", item).Msg("Item updated")
	// Convert models.Item to ogen.Item
	itemOut := ogen.Item{
		ID:        int64(item.ID),
		UUID:      uuid.MustParse(item.UUID),
		CreatedAt: item.CreatedAt,
		Name:      item.Name,
		Price:     item.Price,
	}
	// Compose and return response
	return &ogen.ItemUpdateResponse{
		Data: itemOut,
		Meta: ogen.ItemMeta{
			ItemStatus: ogen.OptItemMetaItemStatus{
				Value: ogen.ItemMetaItemStatusUpdated,
				Set:   true,
			},
		},
	}, nil
}

func (s *ItemsService) DeleteItem(
	ctx context.Context,
	params ogen.DeleteItemParams,
) (ogen.DeleteItemRes, error) {
	log.Info().Interface("DeleteItemParams", params).Msg("Handling item delete request")
	// Delete item
	itemId := params.ItemId
	item, err := itemsrepo.DeleteItem(s.Deps.DBPool, itemId)
	if err != nil {
		log.Error().Err(err).Interface("DeleteItemParams", params).Msg("Error deleting item")
		return nil, s.NewError(ctx, err)
	}
	log.Debug().Interface("item", item).Msg("Item deleted")
	// Return empty response
	return &ogen.DeleteItemNoContent{}, nil
}
