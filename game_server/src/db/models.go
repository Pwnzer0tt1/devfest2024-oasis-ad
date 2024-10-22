package db

import (
	"time"

	"github.com/uptrace/bun"
)

/*
	- Teams are not in the database, they are hardcoded in the configuration file.
	all references to teams are done through their ip address.

	- Services also are not in the database, they are hardcoded in the configuration file.
*/

type FlagIdWrapper struct {
	K interface{} `json:"k"`
}

type Flag struct {
	bun.BaseModel  `bun:"table:flags,alias:flag"`
	ID             string        `bun:",pk"`
	Team           string        `bun:",notnull"`
	Round          uint          `bun:",notnull"`
	Service        string        `bun:",notnull"`
	CreatedAt      time.Time     `bun:",notnull,default:current_timestamp"`
	ExternalFlagId FlagIdWrapper `bun:"type:jsonb"`
}

type FlagSubmission struct {
	bun.BaseModel   `bun:"table:flag_submissions,alias:submit"`
	ID              int64     `bun:",pk,autoincrement"`
	FlagID          string    `bun:",notnull,unique:team"`
	Team            string    `bun:",notnull,unique:team"`
	OffensivePoints float64   `bun:",notnull"`
	DefensivePoints float64   `bun:",notnull"`
	SubmittedAt     time.Time `bun:",notnull,default:current_timestamp"`
	Flag            *Flag     `bun:"rel:belongs-to,join:flag_id=id"`
}

type StatusHistory struct {
	bun.BaseModel  `bun:"table:sla_statues"`
	ID             int64  `bun:",pk,autoincrement"`
	Team           string `bun:",notnull,unique:sla-check"`
	Service        string `bun:",notnull,unique:sla-check"`
	Round          uint   `bun:",notnull,unique:sla-check"`
	PutFlagStatus  int    `bun:",notnull"`
	PutFlagMessage string
	PutFlagAt      time.Time `bun:",notnull"`
	GetFlagStatus  int       `bun:",notnull"`
	GetFlagMessage string
	GetFlagAt      time.Time `bun:",notnull"`
	CheckStatus    int       `bun:",notnull"`
	CheckMessage   string
	CheckdAt       time.Time `bun:",notnull"`
	Sla            float64   `bun:""`
	Score          float64   `bun:""`
	LostFlags      uint      `bun:""`
	StolenFlags    uint      `bun:""`
	SlaUpTimes     uint      `bun:""`
	SlaTotTimes    uint      `bun:""`
}

type ServiceScore struct {
	bun.BaseModel `bun:"table:service_scores"`
	ID            int64   `bun:",pk,autoincrement"`
	Team          string  `bun:",notnull"`
	Service       string  `bun:",notnull"`
	Score         float64 `bun:",notnull"`
}

type Environment struct {
	bun.BaseModel `bun:"table:environments"`
	Key           string `bun:",pk"`
	Value         string `bun:",notnull"`
}

/*

DB ENVIRONMENT VARIABLES

START_TIME - The time the game started
ACTUAL_ROUND_EXPOSED - The current round exposed in the APIs


*/
