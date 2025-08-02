package models

import "time"

// Resource Entity Models

type ItemIn struct {
	Name  string  `json:"name" example:"foo" format:"string" validate:"required"`
	Price float32 `json:"price" example:"3.14" format:"float64" validate:"min=0"`
}

type Item struct {
	ID        int       `json:"id" example:"1" format:"int64"`
	UUID      string    `json:"uuid" example:"550e8400-e29b-41d4-a716-446655440000" format:"uuid"`
	CreatedAt time.Time `json:"created_at" example:"2021-01-01T00:00:00.000Z" format:"date-time"`
	Name      string    `json:"name" example:"foo" format:"string"`
	Price     float32   `json:"price" example:"3.14" format:"float64"`
}

// API Request/Response Models

type StatusResponse struct {
	Status string `json:"status" example:"ok"`
}

type GetItemResponse struct {
	Data *Item    `json:"data"`
	Meta struct{} `json:"meta"`
}

type GetItemsResponse struct {
	Data []*Item  `json:"data"`
	Meta struct{} `json:"meta"`
}

type CreateItemRequest struct {
	Data ItemIn `json:"data"`
}

type CreateItemResponseMeta struct {
	Created bool `json:"created"`
}

type CreateItemResponse struct {
	Data *Item                  `json:"data"`
	Meta CreateItemResponseMeta `json:"meta"`
}
