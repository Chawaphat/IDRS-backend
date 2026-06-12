import os
from collections.abc import Generator

from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres",
)

DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "300"))  # 5 min — Supabase drops idle connections ~10 min
DB_POOL_PRE_PING = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"

engine = create_engine(
    DATABASE_URL,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_timeout=DB_POOL_TIMEOUT,
    pool_recycle=DB_POOL_RECYCLE,
    pool_pre_ping=DB_POOL_PRE_PING,
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
    ensure_occlusal_analysis_schema()
    ensure_residual_ridge_assessment_schema()


def _get_existing_columns(table_name: str) -> set[str]:
    """Query information_schema to get currently existing columns. Fast SELECT only."""
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = :tbl
        """), {"tbl": table_name}).fetchall()
    return {row[0] for row in rows}


def _add_missing_columns(table_name: str, required: dict[str, str]) -> None:
    """Add only columns that don't already exist. Skips completely if nothing is missing."""
    existing = _get_existing_columns(table_name)
    missing = {col: typ for col, typ in required.items() if col not in existing}
    if not missing:
        return
    with engine.begin() as conn:
        for col, typ in missing.items():
            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col} {typ}"))


def ensure_occlusal_analysis_schema() -> None:
    if engine.dialect.name != "postgresql":
        return

    # Create ENUMs — PL/pgSQL duplicate_object exception IS catchable (not a timeout)
    with engine.begin() as conn:
        for ddl in [
            "CREATE TYPE molar_type AS ENUM ('class_i', 'class_ii', 'class_iii')",
            "CREATE TYPE canine_right_type AS ENUM ('class_i', 'class_ii', 'class_iii')",
            "CREATE TYPE canine_left_type AS ENUM ('class_i', 'class_ii', 'class_iii')",
            "CREATE TYPE lateral_direction_type AS ENUM ('right', 'left')",
        ]:
            conn.execute(text(f"""
                DO $$ BEGIN {ddl};
                EXCEPTION WHEN duplicate_object THEN NULL;
                END $$;
            """))

    _add_missing_columns("occlusal_analysis", {
        "right_molar":        "molar_type",
        "left_molar":         "molar_type",
        "overlap_horizontal": "DOUBLE PRECISION",
        "overlap_vertical":   "DOUBLE PRECISION",
        "anterior_slide":     "DOUBLE PRECISION",
        "lateral_slide":      "DOUBLE PRECISION",
        "canine_right":       "canine_right_type",
        "canine_left":        "canine_left_type",
        "lateral_direction":  "lateral_direction_type",
    })


def ensure_residual_ridge_assessment_schema() -> None:
    if engine.dialect.name != "postgresql":
        return

    enum_definitions = {
        "ridge_height_type":         ("high", "low_flat", "knife_edge"),
        "ridge_width_type":          ("round", "narrow"),
        "jaw_size_type":             ("small", "medium", "large"),
        "ridge_shape_upper_type":    ("u_shape", "v_shape", "undercut", "flat"),
        "ridge_shape_lower_type":    ("u_shape", "v_shape", "undercut", "flat"),
        "ridge_relation_type":       ("class_i", "class_ii", "class_iii", "crossbite"),
        "ridge_parallelism_type":    ("parallel", "divergent"),
        "interridge_space_type":     ("sufficient", "insufficient"),
        "arch_form_type":            ("square", "taper", "ovoid"),
        "palatal_vault_type":        ("average", "steep", "v_shape", "shallow"),
        "palatal_throat_form_type":  ("class_i", "class_ii", "class_iii"),
        "tongue_size_type":          ("small", "medium", "large"),
        "tongue_position_type":      ("normal", "retracted"),
        "saliva_amount_type":        ("normal", "xerostomia"),
        "saliva_consistency_type":   ("thick", "thin"),
        "lip_mobility_type":         ("normal", "highly_active", "relatively_inactive"),
        "facial_muscle_tone_type":   ("tense", "average", "flaccid"),
        "mental_attitude_type":      ("philosophical", "exacting", "hysterical", "indifferent"),
    }

    # Create ENUMs — PL/pgSQL duplicate_object exception IS catchable (not a timeout)
    with engine.begin() as conn:
        for enum_name, values in enum_definitions.items():
            quoted_values = ", ".join(f"'{v}'" for v in values)
            conn.execute(text(f"""
                DO $$ BEGIN
                    CREATE TYPE {enum_name} AS ENUM ({quoted_values});
                EXCEPTION WHEN duplicate_object THEN NULL;
                END $$;
            """))

    _add_missing_columns("residual_ridge_assessment", {
        "ridge_height":        "ridge_height_type",
        "ridge_width":         "ridge_width_type",
        "jaw_size":            "jaw_size_type",
        "ridge_shape_upper":   "ridge_shape_upper_type",
        "ridge_shape_lower":   "ridge_shape_lower_type",
        "ridge_relation":      "ridge_relation_type",
        "ridge_parallelism":   "ridge_parallelism_type",
        "interridge_space":    "interridge_space_type",
        "lower_arch_form":     "arch_form_type",
        "palatal_vault":       "palatal_vault_type",
        "palatal_throat_form": "palatal_throat_form_type",
        "freenum_attachment":  "JSONB",
        "ridge_deformity":     "JSONB",
        "torus_palatinus":     "JSONB",
        "tongue_size":         "tongue_size_type",
        "tongue_position":     "tongue_position_type",
        "saliva_amount":       "saliva_amount_type",
        "saliva_consistency":  "saliva_consistency_type",
        "lip_mobility":        "lip_mobility_type",
        "facial_muscle_tone":  "facial_muscle_tone_type",
        "mental_attitude":     "mental_attitude_type",
        "created_at":          "TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()",
        "updated_at":          "TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()",
    })


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
