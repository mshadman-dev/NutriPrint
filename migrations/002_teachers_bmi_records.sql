-- ============================================================
-- 002_teachers_bmi_records.sql
--
-- Adds tables and columns that routers/auth.py, routers/bmi.py,
-- and routers/meals.py reference but are absent from 001_init.sql.
--
-- Safe to re-run: uses IF NOT EXISTS / ADD COLUMN IF NOT EXISTS.
-- All FK columns are nullable so anonymous (no-login) usage keeps
-- working exactly as before.
-- ============================================================


-- ────────────────────────────────────────────────────────────
-- 1. TEACHERS
--    Referenced by: routers/auth.py (every route)
--                   routers/bmi.py  (dashboard_stats, FK source)
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS teachers (
    id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_user_id UUID        UNIQUE NOT NULL,   -- Supabase auth.users.id
    name         TEXT        NOT NULL,
    school_name  TEXT        NOT NULL,
    district     TEXT        NOT NULL DEFAULT '',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Fast lookup by Supabase auth UID (used on every /auth/me call)
CREATE UNIQUE INDEX IF NOT EXISTS teachers_auth_user_id_idx
    ON teachers (auth_user_id);


-- ────────────────────────────────────────────────────────────
-- 2. BMI_RECORDS
--    Referenced by: routers/bmi.py (/calculate, /history,
--                   /export, /dashboard/stats, /dashboard/students,
--                   /class-progress)
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bmi_records (
    id             UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id     UUID        NULL REFERENCES students (id)
                                   ON DELETE CASCADE,
    teacher_id     UUID        NULL REFERENCES teachers (id)
                                   ON DELETE SET NULL,
    height_cm      NUMERIC     NOT NULL,
    weight_kg      NUMERIC     NOT NULL,
    bmi_value      NUMERIC     NOT NULL,
    percentile     NUMERIC     NOT NULL DEFAULT 0,
    z_score        NUMERIC     NOT NULL DEFAULT 0,
    classification TEXT        NOT NULL,   -- underweight|normal|overweight|obese
    advice_en      TEXT        NOT NULL DEFAULT '',
    advice_kn      TEXT        NOT NULL DEFAULT '',
    assessed_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS bmi_records_student_id_idx
    ON bmi_records (student_id);

CREATE INDEX IF NOT EXISTS bmi_records_teacher_id_idx
    ON bmi_records (teacher_id);

-- Chronological queries are always DESC; this index covers both
-- the history fetch and the dashboard "latest per student" sort.
CREATE INDEX IF NOT EXISTS bmi_records_assessed_at_idx
    ON bmi_records (assessed_at DESC);

-- Composite: single query fetches latest records for a teacher
-- in one index scan (used in class_progress and dashboard_stats).
CREATE INDEX IF NOT EXISTS bmi_records_teacher_assessed_idx
    ON bmi_records (teacher_id, assessed_at DESC);


-- ────────────────────────────────────────────────────────────
-- 3. STUDENTS — add missing columns
--    001_init.sql already has: id, teacher_id, name, age, gender,
--    height, weight, bmi, category, created_at
-- ────────────────────────────────────────────────────────────

-- teacher_id FK was declared in 001 without a constraint; add it
-- only if the FK constraint doesn't already exist.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM   information_schema.table_constraints tc
        JOIN   information_schema.key_column_usage  kcu
               ON  tc.constraint_name = kcu.constraint_name
               AND tc.table_name      = kcu.table_name
        WHERE  tc.constraint_type = 'FOREIGN KEY'
        AND    tc.table_name      = 'students'
        AND    kcu.column_name    = 'teacher_id'
    ) THEN
        ALTER TABLE students
            ADD CONSTRAINT students_teacher_id_fkey
            FOREIGN KEY (teacher_id)
            REFERENCES teachers (id)
            ON DELETE SET NULL;
    END IF;
END;
$$;

-- is_active: used in dashboard_students + class_progress with
-- .eq("is_active", True) — all existing rows default to TRUE.
ALTER TABLE students
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;

-- Index for the common query pattern: teacher's active students.
CREATE INDEX IF NOT EXISTS students_teacher_id_idx
    ON students (teacher_id);

CREATE INDEX IF NOT EXISTS students_teacher_active_idx
    ON students (teacher_id, is_active)
    WHERE is_active = TRUE;


-- ────────────────────────────────────────────────────────────
-- 4. MEAL_PLANS — add missing columns
--    001_init.sql already has: id, teacher_id, student_name,
--    plan_json, budget, region, created_at
-- ────────────────────────────────────────────────────────────

-- Scalar fields inserted by routers/meals.py insert_data dict
ALTER TABLE meal_plans
    ADD COLUMN IF NOT EXISTS school_name    TEXT     NULL,
    ADD COLUMN IF NOT EXISTS teacher_name  TEXT     NULL,
    ADD COLUMN IF NOT EXISTS age_group     TEXT     NULL,
    ADD COLUMN IF NOT EXISTS diet_pref     TEXT     NULL,
    ADD COLUMN IF NOT EXISTS strategy      TEXT     NULL,
    ADD COLUMN IF NOT EXISTS bmi_class     TEXT     NULL,
    ADD COLUMN IF NOT EXISTS allergies     JSONB    NOT NULL DEFAULT '[]'::JSONB,
    ADD COLUMN IF NOT EXISTS avg_daily_cal NUMERIC  NULL,
    ADD COLUMN IF NOT EXISTS avg_protein_g NUMERIC  NULL,
    ADD COLUMN IF NOT EXISTS avg_calcium_mg NUMERIC NULL,
    ADD COLUMN IF NOT EXISTS avg_iron_mg   NUMERIC  NULL,
    ADD COLUMN IF NOT EXISTS total_cost_inr NUMERIC NULL,
    ADD COLUMN IF NOT EXISTS generated_by  TEXT     NOT NULL DEFAULT 'groq',
    ADD COLUMN IF NOT EXISTS share_token   TEXT     NULL,
    ADD COLUMN IF NOT EXISTS student_id    UUID     NULL REFERENCES students (id)
                                               ON DELETE SET NULL;

-- teacher_id FK: column already exists in 001; add constraint only
-- if missing (same guard pattern as students above).
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM   information_schema.table_constraints tc
        JOIN   information_schema.key_column_usage  kcu
               ON  tc.constraint_name = kcu.constraint_name
               AND tc.table_name      = kcu.table_name
        WHERE  tc.constraint_type = 'FOREIGN KEY'
        AND    tc.table_name      = 'meal_plans'
        AND    kcu.column_name    = 'teacher_id'
    ) THEN
        ALTER TABLE meal_plans
            ADD CONSTRAINT meal_plans_teacher_id_fkey
            FOREIGN KEY (teacher_id)
            REFERENCES teachers (id)
            ON DELETE SET NULL;
    END IF;
END;
$$;

-- share_token must be unique (used as a public URL slug)
CREATE UNIQUE INDEX IF NOT EXISTS meal_plans_share_token_idx
    ON meal_plans (share_token)
    WHERE share_token IS NOT NULL;

-- Fast lookup for the dashboard "recent plans" and "by teacher" queries
CREATE INDEX IF NOT EXISTS meal_plans_teacher_id_idx
    ON meal_plans (teacher_id);

CREATE INDEX IF NOT EXISTS meal_plans_teacher_created_idx
    ON meal_plans (teacher_id, created_at DESC);

-- student_id for joins (e.g. future per-student plan history)
CREATE INDEX IF NOT EXISTS meal_plans_student_id_idx
    ON meal_plans (student_id)
    WHERE student_id IS NOT NULL;
