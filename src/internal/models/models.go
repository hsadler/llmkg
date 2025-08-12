package models

// Domain Models

type SubjectIn struct {
	Name string
}

type Subject struct {
	ID        string
	Name      string
	KgVersion string
}

type SubjectRelationIn struct {
	SubjectID        string
	RelatedSubjectID string
}

type SubjectRelation struct {
	SubjectID        string
	RelatedSubjectID string
}
