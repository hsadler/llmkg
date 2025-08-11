package main

import (
	"context"
	"fmt"
	"os"
	"time"

	"example-server/internal/openapi/ogen"

	"github.com/fatih/color"
	"github.com/google/uuid"
)

func timeId() int64 {
	return time.Now().UnixNano()
}

func run(ctx context.Context) error {
	client, err := ogen.NewClient("http://localhost:8000")
	if err != nil {
		return fmt.Errorf("failed to create client: %v", err)
	}
	if err := testPing(ctx, client); err != nil {
		return err
	}
	if err := testCreateSubject(ctx, client); err != nil {
		return err
	}
	if err := testGetSubject(ctx, client); err != nil {
		return err
	}
	if err := testCreateSubjectRelation(ctx, client); err != nil {
		return err
	}
	return nil
}

func testPing(ctx context.Context, client *ogen.Client) error {
	resp, err := client.Ping(ctx)
	if err != nil {
		color.New(color.FgRed).Println(err)
		return err
	}
	color.New(color.FgGreen).Println(resp)
	return nil
}

func testCreateSubject(ctx context.Context, client *ogen.Client) error {
	req := &ogen.SubjectCreateRequest{
		Data: ogen.SubjectIn{
			Name: fmt.Sprintf("Subject-%d", timeId()),
		},
	}
	res, err := client.CreateSubject(ctx, req)
	if err != nil {
		color.New(color.FgRed).Println(err)
		return err
	}
	color.New(color.FgGreen).Println(res)
	return nil
}

func testGetSubject(ctx context.Context, client *ogen.Client) error {
	resp, err := client.GetSubject(ctx, ogen.GetSubjectParams{
		SubjectUuid: uuid.MustParse("550e8400-e29b-41d4-a716-446655440000"),
	})
	if err != nil {
		color.New(color.FgRed).Println(err)
		return err
	}
	color.New(color.FgGreen).Println(resp)
	return nil
}

func testCreateSubjectRelation(ctx context.Context, client *ogen.Client) error {
	createSubjectRes, err := client.CreateSubject(ctx, &ogen.SubjectCreateRequest{
		Data: ogen.SubjectIn{
			Name: fmt.Sprintf("Subject-%d", timeId()),
		},
	})
	if err != nil {
		color.New(color.FgRed).Println(err)
		return err
	}
	subjectUuidA := createSubjectRes.(*ogen.SubjectCreateResponse).Data.ID
	createSubjectRes, err = client.CreateSubject(ctx, &ogen.SubjectCreateRequest{
		Data: ogen.SubjectIn{
			Name: fmt.Sprintf("Subject-%d", timeId()),
		},
	})
	if err != nil {
		color.New(color.FgRed).Println(err)
		return err
	}
	subjectUuidB := createSubjectRes.(*ogen.SubjectCreateResponse).Data.ID
	req := &ogen.SubjectRelationCreateRequest{
		Data: ogen.SubjectRelationIn{
			SubjectID:        subjectUuidA,
			RelatedSubjectID: subjectUuidB,
		},
	}
	res, err := client.CreateSubjectRelation(ctx, req)
	if err != nil {
		color.New(color.FgRed).Println(err)
		return err
	}
	color.New(color.FgGreen).Println(res)
	return nil
}

func main() {
	ctx := context.Background()
	err := run(ctx)
	if err != nil {
		os.Exit(2)
	}
}
