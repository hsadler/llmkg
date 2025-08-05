package models

import "time"

// Domain Models

type ItemIn struct {
	Name  string
	Price float32
}

type Item struct {
	ID        int
	UUID      string
	CreatedAt time.Time
	Name      string
	Price     float32
}

type SubjectIn struct {
	Name string
}

type Subject struct {
	ID        int
	UUID      string
	CreatedAt time.Time
	Name      string
}

type SubjectRelationIn struct {
	SubjectID        int
	RelatedSubjectID int
}

type SubjectRelation struct {
	ID               int
	CreatedAt        time.Time
	SubjectID        int
	RelatedSubjectID int
}
