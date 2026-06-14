-- 001_init.sql

CREATE TABLE IF NOT EXISTS students (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  teacher_id UUID NULL,
  name TEXT NOT NULL,
  age INTEGER NOT NULL,
  gender TEXT NOT NULL,
  height DECIMAL NOT NULL,
  weight DECIMAL NOT NULL,
  bmi DECIMAL NOT NULL,
  category TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS meal_plans (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  teacher_id UUID NULL,
  student_name TEXT NOT NULL,
  plan_json JSONB NOT NULL,
  budget DECIMAL NULL,
  region TEXT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS foods (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  calories DECIMAL NOT NULL,
  protein DECIMAL NOT NULL,
  carbs DECIMAL NOT NULL,
  fat DECIMAL NOT NULL,
  category TEXT NOT NULL,
  season TEXT NULL,
  kannada_name TEXT NULL
);

-- Note: In a real Supabase environment, you might also have RLS policies.
-- For this exhibition build, we assume simple authenticated/anon usage via backend.
