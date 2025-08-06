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

type LLMKGService struct {
	Deps *dependencies.Dependencies
}

func (s *LLMKGService) NewError(ctx context.Context, err error) *ogen.ErrorResponseStatusCode {
	return &ogen.ErrorResponseStatusCode{
		StatusCode: http.StatusInternalServerError,
		Response:   ogen.ErrorResponse{Error: err.Error()},
	}
}

func (s *LLMKGService) Ping(
	ctx context.Context,
) (*ogen.PingResponse, error) {
	log.Info().Msg("Handling ping request")
	return &ogen.PingResponse{
		Message: "pong",
	}, nil
}

func (s *LLMKGService) CreateSubject(
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
		ID:                    int64(subject.ID),
		UUID:                  uuid.MustParse(subject.UUID),
		CreatedAt:             subject.CreatedAt,
		Name:                  subject.Name,
		RelatedToSubjectIds:   []int64{},
		RelatedFromSubjectIds: []int64{},
	}
	// Compose and return response
	return &ogen.SubjectCreateResponse{
		Data: subjectOut,
	}, nil
}

func (s *LLMKGService) GetSubjectByName(
	ctx context.Context,
	params ogen.GetSubjectByNameParams,
) (ogen.GetSubjectByNameRes, error) {
	log.Info().Interface("GetSubjectByNameParams", params).Msg("Handling subject by name get request")
	// Fetch subject
	subjectName, ok := params.Name.Get()
	if !ok {
		return nil, &ogen.ErrorResponseStatusCode{
			StatusCode: http.StatusBadRequest,
			Response:   ogen.ErrorResponse{Error: "Name is required"},
		}
	}
	subject, err := repos.FetchSubjectByName(s.Deps.DBPool, subjectName)
	if err != nil {
		log.Error().Err(err).Interface("GetSubjectByNameParams", params).Msg("Error getting subject")
		return nil, s.NewError(ctx, err)
	}
	// Fetch subject relations
	subjectToRelations, err := repos.FetchSubjectRelationsBySubjectId(s.Deps.DBPool, subject.ID)
	if err != nil {
		log.Error().Err(err).Interface("GetSubjectParams", params).Msg("Error getting subject relations")
		return nil, s.NewError(ctx, err)
	}
	log.Debug().Interface("subjectToRelations", subjectToRelations).Msg("Subject to relations fetched")
	subjectFromRelations, err := repos.FetchSubjectRelationsByRelatedSubjectId(s.Deps.DBPool, subject.ID)
	if err != nil {
		log.Error().Err(err).Interface("GetSubjectParams", params).Msg("Error getting subject relations")
		return nil, s.NewError(ctx, err)
	}
	log.Debug().Interface("subjectFromRelations", subjectFromRelations).Msg("Subject from relations fetched")
	// Convert models.Subject to ogen.Subject
	subjectOut := ogen.Subject{
		ID:                    int64(subject.ID),
		UUID:                  uuid.MustParse(subject.UUID),
		CreatedAt:             subject.CreatedAt,
		Name:                  subject.Name,
		RelatedToSubjectIds:   []int64{},
		RelatedFromSubjectIds: []int64{},
	}
	// Compose related subject ids
	for _, subjectRelation := range subjectToRelations {
		subjectOut.RelatedToSubjectIds = append(subjectOut.RelatedToSubjectIds, int64(subjectRelation.RelatedSubjectID))
	}
	for _, subjectRelation := range subjectFromRelations {
		subjectOut.RelatedFromSubjectIds = append(subjectOut.RelatedFromSubjectIds, int64(subjectRelation.SubjectID))
	}
	// Compose and return response
	return &ogen.SubjectGetResponse{
		Data: subjectOut,
	}, nil
}

func (s *LLMKGService) GetSubject(
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
	// Fetch subject relations
	subjectToRelations, err := repos.FetchSubjectRelationsBySubjectId(s.Deps.DBPool, subjectId)
	if err != nil {
		log.Error().Err(err).Interface("GetSubjectParams", params).Msg("Error getting subject relations")
		return nil, s.NewError(ctx, err)
	}
	log.Debug().Interface("subjectToRelations", subjectToRelations).Msg("Subject to relations fetched")
	subjectFromRelations, err := repos.FetchSubjectRelationsByRelatedSubjectId(s.Deps.DBPool, subjectId)
	if err != nil {
		log.Error().Err(err).Interface("GetSubjectParams", params).Msg("Error getting subject relations")
		return nil, s.NewError(ctx, err)
	}
	log.Debug().Interface("subjectFromRelations", subjectFromRelations).Msg("Subject from relations fetched")
	// Convert models.Subject to ogen.Subject
	subjectOut := ogen.Subject{
		ID:                    int64(subject.ID),
		UUID:                  uuid.MustParse(subject.UUID),
		CreatedAt:             subject.CreatedAt,
		Name:                  subject.Name,
		RelatedToSubjectIds:   []int64{},
		RelatedFromSubjectIds: []int64{},
	}
	// Compose related subject ids
	for _, subjectRelation := range subjectToRelations {
		subjectOut.RelatedToSubjectIds = append(subjectOut.RelatedToSubjectIds, int64(subjectRelation.RelatedSubjectID))
	}
	for _, subjectRelation := range subjectFromRelations {
		subjectOut.RelatedFromSubjectIds = append(subjectOut.RelatedFromSubjectIds, int64(subjectRelation.SubjectID))
	}
	// Compose and return response
	return &ogen.SubjectGetResponse{
		Data: subjectOut,
	}, nil
}

func (s *LLMKGService) CreateSubjectRelation(
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
