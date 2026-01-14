"""Initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-01-12 00:00:00

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "runs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("region", sa.String(length=16), nullable=False, index=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
    )
    op.create_index("ix_runs_region", "runs", ["region"])

    op.create_table(
        "trend_snapshots",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("run_id", sa.String(length=36), sa.ForeignKey("runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("region", sa.String(length=16), nullable=False),
        sa.Column("keyword", sa.String(length=256), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("momentum_score", sa.Float(), nullable=False),
        sa.Column("evidence_json", sa.JSON(), nullable=False),
        sa.Column("raw_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("run_id", "keyword", name="uq_trend_run_keyword"),
    )
    op.create_index("ix_trend_snapshots_run_id", "trend_snapshots", ["run_id"])
    op.create_index("ix_trend_snapshots_region", "trend_snapshots", ["region"])

    op.create_table(
        "keywords",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("run_id", sa.String(length=36), sa.ForeignKey("runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_keyword", sa.String(length=256), nullable=False),
        sa.Column("normalized_keyword", sa.String(length=256), nullable=False),
        sa.Column("expansions_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("run_id", "normalized_keyword", name="uq_keyword_run_norm"),
    )
    op.create_index("ix_keywords_run_id", "keywords", ["run_id"])
    op.create_index("ix_keywords_normalized_keyword", "keywords", ["normalized_keyword"])

    op.create_table(
        "makerworld_results",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("run_id", sa.String(length=36), sa.ForeignKey("runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("keyword", sa.String(length=256), nullable=False),
        sa.Column("model_id", sa.String(length=64), nullable=False),
        sa.Column("makerworld_url", sa.String(length=512), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("creator", sa.String(length=256), nullable=False),
        sa.Column("license", sa.String(length=256), nullable=False),
        sa.Column("tags_json", sa.JSON(), nullable=False),
        sa.Column("stats_json", sa.JSON(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_json", sa.JSON(), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("run_id", "keyword", "model_id", name="uq_mw_run_keyword_model"),
    )
    op.create_index("ix_makerworld_results_run_id", "makerworld_results", ["run_id"])
    op.create_index("ix_makerworld_results_keyword", "makerworld_results", ["keyword"])
    op.create_index("ix_mw_run_model", "makerworld_results", ["run_id", "model_id"])

    op.create_table(
        "model_scores",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("run_id", sa.String(length=36), sa.ForeignKey("runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("keyword", sa.String(length=256), nullable=False),
        sa.Column("model_id", sa.String(length=64), nullable=False),
        sa.Column("total_score", sa.Float(), nullable=False),
        sa.Column("verdict", sa.String(length=16), nullable=False),
        sa.Column("scores_json", sa.JSON(), nullable=False),
        sa.Column("notes_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("run_id", "keyword", "model_id", name="uq_score_run_keyword_model"),
    )
    op.create_index("ix_model_scores_run_id", "model_scores", ["run_id"])
    op.create_index("ix_model_scores_keyword", "model_scores", ["keyword"])
    op.create_index("ix_model_scores_model_id", "model_scores", ["model_id"])

    op.create_table(
        "recommendations",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("run_id", sa.String(length=36), sa.ForeignKey("runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("keyword", sa.String(length=256), nullable=False),
        sa.Column("model_id", sa.String(length=64), nullable=False),
        sa.Column("report_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("run_id", "rank", name="uq_rec_run_rank"),
    )
    op.create_index("ix_recommendations_run_id", "recommendations", ["run_id"])
    op.create_index("ix_rec_run_rank", "recommendations", ["run_id", "rank"])

    op.create_table(
        "http_cache",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("url", sa.String(length=1024), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("headers_json", sa.JSON(), nullable=False),
        sa.Column("content_type", sa.String(length=128), nullable=False),
        sa.Column("body_bytes", sa.LargeBinary(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("url", "request_hash", name="uq_cache_url_hash"),
    )
    op.create_index("ix_cache_expires", "http_cache", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_cache_expires", table_name="http_cache")
    op.drop_table("http_cache")

    op.drop_index("ix_rec_run_rank", table_name="recommendations")
    op.drop_index("ix_recommendations_run_id", table_name="recommendations")
    op.drop_table("recommendations")

    op.drop_index("ix_model_scores_model_id", table_name="model_scores")
    op.drop_index("ix_model_scores_keyword", table_name="model_scores")
    op.drop_index("ix_model_scores_run_id", table_name="model_scores")
    op.drop_table("model_scores")

    op.drop_index("ix_mw_run_model", table_name="makerworld_results")
    op.drop_index("ix_makerworld_results_keyword", table_name="makerworld_results")
    op.drop_index("ix_makerworld_results_run_id", table_name="makerworld_results")
    op.drop_table("makerworld_results")

    op.drop_index("ix_keywords_normalized_keyword", table_name="keywords")
    op.drop_index("ix_keywords_run_id", table_name="keywords")
    op.drop_table("keywords")

    op.drop_index("ix_trend_snapshots_region", table_name="trend_snapshots")
    op.drop_index("ix_trend_snapshots_run_id", table_name="trend_snapshots")
    op.drop_table("trend_snapshots")

    op.drop_index("ix_runs_region", table_name="runs")
    op.drop_table("runs")
import os
from datetime import datetime

os.makedirs("reports", exist_ok=True)

ts = datetime.utcnow().strftime("%Y%m%d_%H%M")
path = f"reports/report_{ts}.md"

with open(path, "w") as f:
    f.write("# Daily Trend → MakerWorld Report\n\n")
    f.write("Pipeline ran successfully.\n")
