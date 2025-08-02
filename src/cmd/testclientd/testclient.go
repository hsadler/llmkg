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
	if err := testCreateItem(ctx, client); err != nil {
		return err
	}
	if err := testGetItem(ctx, client); err != nil {
		return err
	}
	if err := testUpdateItem(ctx, client); err != nil {
		return err
	}
	if err := testDeleteItem(ctx, client); err != nil {
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

func testCreateItem(ctx context.Context, client *ogen.Client) error {
	req := &ogen.ItemCreateRequest{
		Data: ogen.ItemIn{
			Name:  fmt.Sprintf("Item-%d", timeId()),
			Price: 19.99,
		},
	}
	res, err := client.CreateItem(ctx, req)
	if err != nil {
		color.New(color.FgRed).Println(err)
		return err
	}
	color.New(color.FgGreen).Println(res)
	return nil
}

func testGetItem(ctx context.Context, client *ogen.Client) error {
	resp, err := client.GetItem(ctx, ogen.GetItemParams{
		ItemId: 1,
	})
	if err != nil {
		color.New(color.FgRed).Println(err)
		return err
	}
	color.New(color.FgGreen).Println(resp)
	return nil
}

func testUpdateItem(ctx context.Context, client *ogen.Client) error {
	req := &ogen.ItemUpdateRequest{
		Data: ogen.ItemIn{
			Name:  fmt.Sprintf("Updated Item-%d", timeId()),
			Price: 29.99,
		},
	}
	resp, err := client.UpdateItem(
		ctx,
		req,
		ogen.UpdateItemParams{
			ItemId: 1,
		},
	)
	if err != nil {
		color.New(color.FgRed).Println(err)
		return err
	}
	color.New(color.FgGreen).Println(resp)
	return nil
}

func testDeleteItem(ctx context.Context, client *ogen.Client) error {
	createRes, err := client.CreateItem(ctx, &ogen.ItemCreateRequest{
		Data: ogen.ItemIn{
			Name:  fmt.Sprintf("Item-%d", timeId()),
			Price: 19.99,
		},
	})
	if err != nil {
		color.New(color.FgRed).Println("Error creating item for delete:", err)
		return err
	}
	itemCreated := createRes.(*ogen.ItemCreateResponse).Data
	deleteRes, err := client.DeleteItem(ctx, ogen.DeleteItemParams{
		ItemId: int(itemCreated.ID),
	})
	if err != nil {
		color.New(color.FgRed).Println("Error deleting item:", err)
		return err
	}
	color.New(color.FgGreen).Println(deleteRes)
	return nil
}

func main() {
	ctx := context.Background()
	err := run(ctx)
	if err != nil {
		color.New(color.FgRed).Println(err)
		os.Exit(2)
	}
}
