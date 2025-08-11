package main

import (
	"context"
	"fmt"
	"os"
	"time"

	"example-server/internal/openapi/ogen"

	"github.com/fatih/color"
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
	if err := testSubject(ctx, client); err != nil {
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

func testSubject(ctx context.Context, client *ogen.Client) error {
	// Create subject
	createRes, err := client.CreateSubject(
		ctx,
		&ogen.SubjectCreateRequest{
			Data: ogen.SubjectIn{
				Name: fmt.Sprintf("Subject-%d", timeId()),
			},
		},
	)
	if err != nil {
		color.New(color.FgRed).Println(err)
		return err
	}
	subjA := createRes.(*ogen.SubjectCreateResponse).Data
	color.New(color.FgCyan).Println("Subject created")
	color.New(color.FgGreen).Println(createRes)
	// Get subject
	getRes, err := client.GetSubjectByName(ctx, ogen.GetSubjectByNameParams{
		Name: createRes.(*ogen.SubjectCreateResponse).Data.Name,
	})
	if err != nil {
		color.New(color.FgRed).Println(err)
		return err
	}
	color.New(color.FgCyan).Println("Subject retrieved")
	color.New(color.FgGreen).Println(getRes)
	// Create 2nd subject
	createRes, err = client.CreateSubject(
		ctx,
		&ogen.SubjectCreateRequest{
			Data: ogen.SubjectIn{
				Name: fmt.Sprintf("Subject-%d", timeId()),
			},
		},
	)
	if err != nil {
		color.New(color.FgRed).Println(err)
		return err
	}
	color.New(color.FgCyan).Println("2nd subject created")
	color.New(color.FgGreen).Println(createRes)
	subjB := createRes.(*ogen.SubjectCreateResponse).Data
	// Create subject relation
	createSubjectRelationRes, err := client.CreateSubjectRelation(
		ctx,
		&ogen.SubjectRelationCreateRequest{
			Data: ogen.SubjectRelationIn{
				SubjectID:        subjA.ID,
				RelatedSubjectID: subjB.ID,
			},
		},
	)
	if err != nil {
		color.New(color.FgRed).Println(err)
		return err
	}
	color.New(color.FgGreen).Println("Subject relation created")
	color.New(color.FgGreen).Println(createSubjectRelationRes)
	return nil
}

func main() {
	ctx := context.Background()
	err := run(ctx)
	if err != nil {
		os.Exit(2)
	}
}
