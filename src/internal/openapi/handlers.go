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
	kgVersion := string(req.KgVersion)
	subjectOut, err := repos.CreateSubjectNode(s.Deps.Neo4jDriver, kgVersion, subjectIn.Name)
	if err != nil {
		log.Error().Err(err).Interface("SubjectCreateRequest", req).Msg("Error creating subject")
		return nil, s.NewError(ctx, err)
	}
	log.Debug().Interface("subjectOut", subjectOut).Msg("Subject created")
	subject := ogen.Subject{
		ID:   subjectOut.ID,
		Name: subjectOut.Name,
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
	subjectName := params.Name
	kgVersion := string(params.KgVersion)
	subjectOut, err := repos.GetSubjectByName(s.Deps.Neo4jDriver, kgVersion, subjectName)
	if err != nil {
		log.Error().Err(err).Interface("GetSubjectByNameParams", params).Msg("Error getting subject by name")
		return nil, s.NewError(ctx, err)
	}
	// Compose and return response
	return &ogen.SubjectGetResponse{
		Data: ogen.Subject{
			ID:   subjectOut.ID,
			Name: subjectOut.Name,
		},
	}, nil
}

func (s *LLMKGService) CreateSubjectRelation(
	ctx context.Context,
	req *ogen.SubjectRelationCreateRequest,
) (ogen.CreateSubjectRelationRes, error) {
	log.Info().Interface("SubjectRelationCreateRequest", req).Msg("Handling subject relation create request")
	subjectRelationIn := req.Data
	kgVersion := req.KgVersion
	subjectRelationOut, err := repos.CreateSubjectRelation(
		s.Deps.Neo4jDriver,
		string(kgVersion),
		subjectRelationIn.SubjectID,
		subjectRelationIn.RelatedSubjectID,
	)
	if err != nil {
		log.Error().Err(err).Interface("SubjectRelationCreateRequest", req).Msg("Error creating subject relation")
		return nil, s.NewError(ctx, err)
	}
	log.Debug().Interface("subjectRelationOut", subjectRelationOut).Msg("Subject relation created")
	return &ogen.SubjectRelationCreateResponse{
		Data: ogen.SubjectRelation{
			SubjectID:        subjectRelationOut.SubjectID,
			RelatedSubjectID: subjectRelationOut.RelatedSubjectID,
		},
	}, nil
}

func (s *LLMKGService) TruncateTables(
	ctx context.Context,
) error {
	log.Info().Msg("Handling truncate tables request")
	err := repos.TruncateNeo4j(s.Deps.Neo4jDriver)
	if err != nil {
		log.Error().Err(err).Msg("Error truncating tables")
		return s.NewError(ctx, err)
	}
	log.Info().Msg("Tables truncated")
	return nil
}
