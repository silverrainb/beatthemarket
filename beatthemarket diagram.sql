-- Exported from QuickDBD: https://www.quickdatabasediagrams.com/
-- Link to schema: https://app.quickdatabasediagrams.com/#/d/OzfWQE
-- NOTE! If you have used non-SQL datatypes in your design, you will have to change these here.


CREATE TABLE "Users" (
    "id" INT   NOT NULL,
    "email" TEXT   NOT NULL,
    "password" TEXT   NOT NULL,
    "created_at" DATE   NOT NULL,
    CONSTRAINT "pk_Users" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "Holdings" (
    "id" INT   NOT NULL,
    "user_id" INT   NOT NULL,
    "type" TEXT   NOT NULL,
    "ticker" TEXT   NOT NULL,
    "quantity" INT   NOT NULL,
    "price" INT   NOT NULL,
    "date" DATE   NOT NULL,
    CONSTRAINT "pk_Holdings" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "MarketSummary" (
    "id" INT   NOT NULL,
    "timestamp" DATE   NOT NULL,
    "data" JSONB   NOT NULL,
    CONSTRAINT "pk_MarketSummary" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "CurrentPrice" (
    "id" INT   NOT NULL,
    "timestamp" DATE   NOT NULL,
    "data" JSONB   NOT NULL,
    CONSTRAINT "pk_CurrentPrice" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "PL" (
    "id" INT   NOT NULL,
    "user_id" INT   NOT NULL,
    "timestamp" DATE   NOT NULL,
    "data" JSONB   NOT NULL,
    CONSTRAINT "pk_PL" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "Insight" (
    "id" INT   NOT NULL,
    "ticker" STRING   NOT NULL,
    "data" JSONB   NOT NULL,
    CONSTRAINT "pk_Insight" PRIMARY KEY (
        "id"
     )
);

ALTER TABLE "Holdings" ADD CONSTRAINT "fk_Holdings_user_id" FOREIGN KEY("user_id")
REFERENCES "Users" ("id");

ALTER TABLE "PL" ADD CONSTRAINT "fk_PL_user_id" FOREIGN KEY("user_id")
REFERENCES "Users" ("id");

