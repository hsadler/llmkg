package openapi

import (
	"context"
	"net/http"

	"github.com/rs/zerolog/log"

	"example-server/internal/dependencies"
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
	subjectOut, err := repos.CreateSubjectNode(s.Deps.Neo4jDriver, subjectIn.Name)
	if err != nil {
		log.Error().Err(err).Interface("SubjectCreateRequest", req).Msg("Error creating subject")
		return nil, s.NewError(ctx, err)
	}
	log.Debug().Interface("subjectOut", subjectOut).Msg("Subject created")
	subject := ogen.Subject{
		ID:                    subjectOut.ID,
		Name:                  subjectOut.Name,
		RelatedToSubjectIds:   []string{},
		RelatedFromSubjectIds: []string{},
	}
	// Compose and return response
	return &ogen.SubjectCreateResponse{
		Data: subject,
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
	// TODO: Implement Neo4j query
	// MOCK DATA
	subjectOut := ogen.Subject{
		ID:                    "4:16987f9f-8033-4cd6-a7c6-94493f1f20ba:12",
		Name:                  subjectName,
		RelatedToSubjectIds:   []string{},
		RelatedFromSubjectIds: []string{},
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
	// TODO: Implement Neo4j query
	// MOCK DATA
	subjectOut := ogen.Subject{
		ID:                    "4:16987f9f-8033-4cd6-a7c6-94493f1f20ba:12",
		Name:                  "Artificial Intelligence",
		RelatedToSubjectIds:   []string{},
		RelatedFromSubjectIds: []string{},
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
	// TODO: Implement Neo4j query
	// MOCK DATA
	subjectRelationOut := ogen.SubjectRelation{
		SubjectID:        "4:16987f9f-8033-4cd6-a7c6-94493f1f20ba:12",
		RelatedSubjectID: "4:16987f9f-8033-4cd6-a7c6-94493f1f20ba:12",
	}
	// Compose and return response
	return &ogen.SubjectRelationCreateResponse{
		Data: subjectRelationOut,
	}, nil
}

func (s *LLMKGService) TruncateTables(
	ctx context.Context,
) error {
	log.Info().Msg("Handling truncate tables request")
	err := repos.TruncateTables(s.Deps.DBPool)
	if err != nil {
		log.Error().Err(err).Msg("Error truncating tables")
		return s.NewError(ctx, err)
	}
	log.Info().Msg("Tables truncated")
	return nil
}
