# NutriPrint V2

AI-powered school nutrition platform for Karnataka, India — designed to assess child growth, generate personalised 7-day meal plans, and produce shareable health posters for students aged 5–15.

## Overview

Malnutrition and stunting remain significant concerns in Karnataka's government and aided schools. NutriPrint V2 gives teachers a practical tool to assess each student's BMI against IAP (Indian Academy of Pediatrics) growth charts, then immediately generate a context-aware, culturally appropriate meal plan using the Groq LLM API. The system respects regional food traditions, diet preferences (vegetarian / eggetarian / non-vegetarian), seasonal availability, and ICMR RDA nutritional targets — all without requiring any nutrition expertise from the teacher.

The output is a shareable web poster and downloadable PDF report that parents and school administrators can act on. Because the tool runs entirely through a browser — no app install required — it is suited for schools with limited infrastructure.

## Key Features

- **BMI Assessment with IAP Percentile Tables** — Calculates BMI, percentile, and z-score for children aged 5–15 using sex-specific IAP growth charts. Classifies students as underweight, normal, overweight, or obese, and returns bilingual advice (English + ಕನ್ನಡ).
- **AI 7-Day Meal Planning (Groq `llama-3.1-8b-instant`)** — Generates a structured weekly meal plan via Groq, with breakfast, lunch, and dinner for each day. Includes per-meal calorie, protein, calcium, and iron estimates. A built-in fallback engine ensures a plan is always returned even when the Groq API is unavailable.
- **Diet-Compliance Filtering** — All meal plans and food suggestions are filtered against the student's declared diet preference. Non-compliant items are automatically replaced with appropriate substitutes before the plan is returned.
- **Nutrition Gap Analysis** — Compares a generated plan's average daily intake against ICMR RDA targets for the student's age group (5–8, 9–12, 13–15) and surfaces critical deficiencies (calories, protein, calcium, iron) with food-specific fix suggestions in English and Kannada.
- **Food Catalog** — Searchable, filterable catalog of Karnataka-region foods loaded from a local JSON dataset. Supports filtering by diet type, category, meal type, region, and nutritional highlight. Each food links to a full recipe page with ingredients and preparation steps.
- **Shareable Posters & PDF Reports** — Every generated plan gets a unique share token. The public poster page (`/plan/<token>`) is a printable, mobile-friendly view. The health report page (`/report/<token>`) provides a deeper breakdown. A PDF download is available via ReportLab.
- **QR Codes** — Generates a PNG QR code for any plan's public URL, making it easy to share with parents on print-outs or WhatsApp.
- **Teacher Dashboard** — Logged-in teachers see aggregated stats for their class: total students assessed, BMI distribution, health score benchmarked against a Karnataka average, average percentile, and a list of students needing attention. Recent plans and a CSV export of all BMI records are also available.
- **Per-Day Meal Regeneration** — Individual days in a saved plan can be regenerated without replacing the full week.

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI 0.136 |
| Database & Auth | Supabase (PostgreSQL + GoTrue) |
| AI / LLM | Groq API — `llama-3.1-8b-instant` |
| PDF generation | ReportLab 4.5 |
| QR code generation | qrcode 8.2 |
| Templates | Jinja2 3.1 |
| Frontend styling | Tailwind CSS (CDN) |
| Server | Uvicorn + Gunicorn |
| Python | 3.11+ |

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/nutriprint-v2.git
cd nutriprint-v2
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the `.env` file

Copy the example below into a file named `.env` in the project root and fill in your values:

```env
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
SECRET_KEY=a_long_random_secret_string
ADMIN_TOKEN=your_admin_token
ENVIRONMENT=development
CORS_ORIGINS=*
```

| Variable | Purpose |
|---|---|
| `GROQ_API_KEY` | API key for the Groq LLM service |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Supabase anon/public key (used by the app layer) |
| `SUPABASE_SERVICE_KEY` | Supabase service role key (used for server-side operations) |
| `SECRET_KEY` | Secret used for session signing |
| `ADMIN_TOKEN` | Token for admin-protected routes |
| `ENVIRONMENT` | Set to `production` to enable secure cookies; default is `development` |
| `CORS_ORIGINS` | Comma-separated list of allowed origins, or `*` to allow all |

### 5. Run database migrations

Run the two migration files against your Supabase project using the Supabase SQL editor or `psql`:

```sql
-- Run in order:
\i migrations/001_init.sql
\i migrations/002_teachers_bmi_records.sql
```

`001_init.sql` creates the core `students`, `meal_plans`, and `foods` tables. `002_teachers_bmi_records.sql` adds the `teachers` and `bmi_records` tables needed for the teacher dashboard and BMI history tracking.

### 6. Start the development server

```bash
uvicorn main:app --reload
```

The app will be available at `http://localhost:8000`. Interactive API docs are at `http://localhost:8000/docs`.

## Project Structure

```
nutriprint-v2/
├── main.py                  # FastAPI app factory, route mounts, page routes
├── config.py                # Environment variable loading
├── routers/                 # API and page route handlers
│   ├── auth.py              # OTP login, session verification, teacher profile
│   ├── bmi.py               # BMI calculation, history, dashboard, CSV export
│   ├── meals.py             # Meal plan generation, retrieval by share token
│   ├── foods.py             # Food catalog search and impact stats
│   ├── recipes.py           # Per-food recipe page (HTML)
│   ├── ai_advisor.py        # Conversational nutrition advisor (Groq)
│   ├── poster.py            # Public plan page, health report, PDF, QR code
│   └── deps.py              # Shared auth dependencies and error helpers
├── services/                # Business logic and integrations
│   ├── bmi_calculator.py    # IAP percentile tables, BMI classification, ICMR RDA
│   ├── groq_engine.py       # Groq LLM prompting for meal plans and AI advisor
│   ├── fallback_engine.py   # Rule-based fallback plan generator
│   ├── diet_filter.py       # Diet compliance rules, substitutions, strategy notes
│   ├── food_equivalents.py  # Serving-size examples for nutrient targets
│   ├── food_images.py       # Food image resolution helpers
│   ├── poster_context.py    # Builds template context for poster/report pages
│   └── pdf_generator.py     # ReportLab PDF generation for meal plan reports
├── models/
│   ├── schemas.py           # Pydantic request/response models
│   └── db.py                # Supabase client initialisation
├── templates/               # Jinja2 HTML templates (login, BMI, meal planner,
│   │                        #   dashboard, poster, report, recipe, etc.)
├── static/
│   ├── css/                 # Feature-specific stylesheets
│   ├── images/foods/        # Local food photography (74 images)
│   └── js/                  # Frontend JavaScript modules
├── data/
│   ├── foods.json           # Full Karnataka food dataset with nutrition data
│   └── recipes.json         # Ingredients and preparation steps per food
└── migrations/
    ├── 001_init.sql         # Initial schema: students, meal_plans, foods
    └── 002_teachers_bmi_records.sql  # Teachers and BMI records tables
```

## API Endpoints

### Authentication — `/auth`

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/login` | Send OTP to teacher's email via Supabase |
| `POST` | `/auth/verify` | Verify OTP, set session cookie |
| `POST` | `/auth/profile` | Create teacher profile after first login |
| `POST` | `/auth/logout` | Clear session cookie |
| `GET` | `/api/auth/me` | Return current session and teacher profile |

### BMI — `/api/bmi`

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/bmi/calculate` | Calculate BMI, classify against IAP tables, save to DB |
| `GET` | `/api/bmi/history/{student_id}` | BMI measurement history for a student |
| `GET` | `/api/bmi/export/{teacher_id}` | Download all BMI records as CSV |
| `GET` | `/api/bmi/nutrition-gap` | Nutrition gap analysis for a saved plan |
| `GET` | `/api/bmi/food-equivalents` | Serving-size examples for nutrient targets |
| `GET` | `/api/bmi/dashboard/stats` | Aggregate stats for teacher dashboard |
| `GET` | `/api/bmi/dashboard/students` | Student list with latest BMI for dashboard |
| `GET` | `/api/bmi/dashboard/recent-plans` | 5 most recent meal plans for the teacher |
| `GET` | `/api/bmi/class-progress` | Class-wide BMI distribution, health score, recommendations |

### Meal Plans — `/api/meal`

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/meal/generate` | Generate a 7-day meal plan (Groq, with fallback) |
| `PATCH` | `/api/meal/{plan_id}/day` | Regenerate a single day in an existing plan |
| `GET` | `/api/meal/by-token/{share_token}` | Fetch a saved plan by share token |

### Foods — `/api/foods`

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/foods` | Search and filter the food catalog (paginated) |
| `GET` | `/api/foods/impact` | Platform impact stats (total plans, students, foods) |

### AI Advisor — `/api/ai-advisor`

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/ai-advisor/chat` | Ask the nutrition advisor a question (Groq, bilingual) |

### Poster & Reports — (no prefix)

| Method | Path | Description |
|---|---|---|
| `GET` | `/plan/{share_token}` | Public shareable meal plan poster (HTML) |
| `GET` | `/report/{share_token}` | Full health report page (HTML) |
| `GET` | `/poster/{share_token}/print` | Print-optimised poster view |
| `GET` | `/poster/{share_token}/pdf` | Download plan as PDF (ReportLab) |
| `GET` | `/api/plans/qr` | Generate QR code PNG for a plan URL |

### Recipes — (no prefix)

| Method | Path | Description |
|---|---|---|
| `GET` | `/recipes/{food_name}` | Recipe page for a single food item (HTML) |

### Pages & Health

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Home page |
| `GET` | `/login` | Login page |
| `GET` | `/bmi` | BMI assessment page |
| `GET` | `/meal-planner` | Meal planner page |
| `GET` | `/food-catalog` | Food catalog page |
| `GET` | `/dashboard` | Teacher dashboard |
| `GET` | `/about` | About page |
| `GET` | `/ping` | Health check — returns `{"status": "ok"}` |

## Access

The login page lets any user access the full platform instantly — no registration or email OTP required. A client-side session is written to `localStorage` on the first visit, granting access to BMI assessment, meal planning, food catalog, poster generation, and the teacher dashboard.

> **Note:** The Supabase OTP authentication backend is implemented but not yet wired to the production frontend UI. Client-side session state is the current access path for this build.

## Credits

NutriPrint V2 was developed as a final-year B.E. project at **Yenepoya Institute of Technology**, Moodbidri, Karnataka, affiliated with **Visvesvaraya Technological University (VTU)**, Belagavi.

The project aims to address child malnutrition in Karnataka government schools by combining IAP-standard growth assessment with AI-assisted, culturally grounded meal planning — all accessible to teachers without nutritional training.

Nutrition reference data sourced from:
- Indian Academy of Pediatrics (IAP) growth charts for BMI-for-age percentiles
- Indian Council of Medical Research (ICMR) Recommended Dietary Allowances

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for the full text.

Copyright © 2026 Mohammed Shadman
