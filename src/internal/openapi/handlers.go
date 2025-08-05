package openapi

import (
	"context"
	"net/http"

	"github.com/google/uuid"
	"github.com/rs/zerolog/log"

	"example-server/internal/dependencies"
	"example-server/internal/models"
	"example-server/internal/openapi/ogen"
	"example-server/internal/repos"
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
	item, err := repos.InsertItem(s.Deps.DBPool, models.ItemIn{
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
	item, err := repos.FetchItemById(s.Deps.DBPool, itemId)
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
	item, err := repos.UpdateItem(s.Deps.DBPool, itemId, models.ItemIn{
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
	item, err := repos.DeleteItem(s.Deps.DBPool, itemId)
	if err != nil {
		log.Error().Err(err).Interface("DeleteItemParams", params).Msg("Error deleting item")
		return nil, s.NewError(ctx, err)
	}
	log.Debug().Interface("item", item).Msg("Item deleted")
	// Return empty response
	return &ogen.DeleteItemNoContent{}, nil
}

func (s *ItemsService) CreateSubject(
	ctx context.Context,
	req *ogen.SubjectCreateRequest,
) (ogen.CreateSubjectRes, error) {
	log.Info().Interface("SubjectCreateRequest", req).Msg("Handling subject create request")
	subjectIn := req.Data
	subject, err := repos.InsertSubject(s.Deps.DBPool, models.SubjectIn{
		Name: subjectIn.Name,
	})
	if err != nil {
		log.Error().Err(err).Interface("SubjectCreateRequest", req).Msg("Error inserting subject")
		if err == repos.ErrorSubjectExists {
			return nil, &ogen.ErrorResponseStatusCode{
				StatusCode: http.StatusConflict,
				Response:   ogen.ErrorResponse{Error: err.Error()},
			}
		}
		return nil, s.NewError(ctx, err)
	}
	log.Debug().Interface("subject", subject).Msg("Subject created")
	// Convert models.Subject to ogen.Subject
	subjectOut := ogen.Subject{
		ID:        int64(subject.ID),
		UUID:      uuid.MustParse(subject.UUID),
		CreatedAt: subject.CreatedAt,
		Name:      subject.Name,
	}
	// Compose and return response
	return &ogen.SubjectCreateResponse{
		Data: subjectOut,
	}, nil
}

func (s *ItemsService) GetSubject(
	ctx context.Context,
	params ogen.GetSubjectParams,
) (ogen.GetSubjectRes, error) {
	log.Info().Interface("GetSubjectParams", params).Msg("Handling subject get request")
	// Fetch subject
	subjectId := params.SubjectId
	subject, err := repos.FetchSubjectById(s.Deps.DBPool, subjectId)
	if err != nil {
		log.Error().Err(err).Interface("GetSubjectParams", params).Msg("Error getting subject")
		return nil, s.NewError(ctx, err)
	}
	log.Debug().Interface("subject", subject).Msg("Subject fetched")
	// Convert models.Subject to ogen.Subject
	subjectOut := ogen.Subject{
		ID:        int64(subject.ID),
		UUID:      uuid.MustParse(subject.UUID),
		CreatedAt: subject.CreatedAt,
		Name:      subject.Name,
	}
	// Compose and return response
	return &ogen.SubjectGetResponse{
		Data: subjectOut,
	}, nil
}

func (s *ItemsService) CreateSubjectRelation(
	ctx context.Context,
	req *ogen.SubjectRelationCreateRequest,
) (ogen.CreateSubjectRelationRes, error) {
	log.Info().Interface("SubjectRelationCreateRequest", req).Msg("Handling subject relation create request")
	subjectRelationIn := req.Data
	subjectRelation, err := repos.InsertSubjectRelation(s.Deps.DBPool, models.SubjectRelationIn{
		SubjectID:        int(subjectRelationIn.SubjectID),
		RelatedSubjectID: int(subjectRelationIn.RelatedSubjectID),
	})
	if err != nil {
		log.Error().Err(err).Msg("Error creating subject relation")
		if err == repos.ErrorSubjectRelationExists {
			return nil, &ogen.ErrorResponseStatusCode{
				StatusCode: http.StatusConflict,
				Response:   ogen.ErrorResponse{Error: err.Error()},
			}
		}
		return nil, s.NewError(ctx, err)
	}
	log.Debug().Interface("subjectRelation", subjectRelation).Msg("Subject relation created")
	// Convert models.SubjectRelation to ogen.SubjectRelation
	subjectRelationOut := ogen.SubjectRelation{
		ID:               int64(subjectRelation.ID),
		CreatedAt:        subjectRelation.CreatedAt,
		SubjectID:        int64(subjectRelation.SubjectID),
		RelatedSubjectID: int64(subjectRelation.RelatedSubjectID),
	}
	// Compose and return response
	return &ogen.SubjectRelationCreateResponse{
		Data: subjectRelationOut,
	}, nil
}
