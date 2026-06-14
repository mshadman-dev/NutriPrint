from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from models.schemas import BMIInput, BMIResult
from models.db import supabase
from services.bmi_calculator import calculate_bmi, calculate_nutrition_gap
from services.food_equivalents import get_food_equivalents
from routers.deps import require_teacher_access, safe_error_detail
from datetime import datetime

router = APIRouter(prefix="/api/bmi", tags=["BMI"])


# ── Calculate BMI ─────────────────────────────────────────
@router.post("/calculate", response_model=BMIResult)
async def bmi_calculate(data: BMIInput):
    # Step 1: Calculate BMI — must succeed or we return 500.
    try:
        result = calculate_bmi(
            student_name = data.student_name,
            age          = data.age,
            gender       = data.gender.value,
            height_cm    = data.height_cm,
            weight_kg    = data.weight_kg,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=safe_error_detail(e))

    # Step 2: Persist to DB — failures are logged but do NOT block the response.
    student_id: str | None = None
    try:
        student_data = {
            "name"    : data.student_name,
            "age"     : data.age,
            "gender"  : data.gender.value,
            "height"  : data.height_cm,
            "weight"  : data.weight_kg,
            "bmi"     : float(result.bmi_value),
            "category": result.classification.value,
        }
        if data.teacher_id:
            student_data["teacher_id"] = data.teacher_id

        student_res = supabase.table("students").insert(student_data).execute()
        student_id = student_res.data[0]["id"] if student_res.data else None
    except Exception as e:
        # Non-fatal: DB unavailable or RLS blocked the insert.
        print(f"[bmi_calculate] students insert failed (non-fatal): {e}")

    try:
        if data.teacher_id and student_id:
            supabase.table("bmi_records").insert({
                "student_id"     : student_id,
                "teacher_id"     : data.teacher_id,
                "height_cm"      : data.height_cm,
                "weight_kg"      : data.weight_kg,
                "bmi_value"      : float(result.bmi_value),
                "percentile"     : float(result.percentile),
                "z_score"        : float(result.z_score),
                "classification" : result.classification.value,
                "advice_en"      : result.advice_en,
                "advice_kn"      : result.advice_kn,
            }).execute()
    except Exception as e:
        # Non-fatal: FK violation if teacher_id is stale/invalid.
        print(f"[bmi_calculate] bmi_records insert failed (non-fatal): {e}")

    return result


# ── BMI History ───────────────────────────────────────────
@router.get("/history/{student_id}")
async def bmi_history(student_id: str, request: Request):
    try:
        student = (
            supabase.table("students")
            .select("teacher_id")
            .eq("id", student_id)
            .single()
            .execute()
        )
        if not student.data:
            raise HTTPException(status_code=404, detail="Student not found")

        await require_teacher_access(request, student.data["teacher_id"])

        result = supabase.table("bmi_records")\
            .select("*")\
            .eq("student_id", student_id)\
            .order("assessed_at", desc=False)\
            .execute()
        return {"history": result.data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=safe_error_detail(e))


# ── Export CSV ────────────────────────────────────────────
@router.get("/export/{teacher_id}")
async def export_csv(teacher_id: str, request: Request):
    try:
        await require_teacher_access(request, teacher_id)
        import csv
        import io

        records = supabase.table("bmi_records")\
            .select("*, students(name, age, gender)")\
            .eq("teacher_id", teacher_id)\
            .order("assessed_at", desc=True)\
            .execute()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Student Name", "Age", "Gender",
            "Height(cm)", "Weight(kg)", "BMI",
            "Percentile", "Classification", "Date"
        ])

        for r in records.data:
            s = r.get("students", {}) or {}
            writer.writerow([
                s.get("name", ""),
                s.get("age", ""),
                s.get("gender", ""),
                r["height_cm"],
                r["weight_kg"],
                r["bmi_value"],
                r["percentile"],
                r["classification"],
                r["assessed_at"][:10],
            ])

        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type = "text/csv",
            headers    = {
                "Content-Disposition":
                    "attachment; filename=bmi_records.csv"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=safe_error_detail(e))


# ── Nutrition Gap ─────────────────────────────────────────
@router.get("/nutrition-gap")
async def nutrition_gap(plan_id: str, age_group: str, diet_pref: str = ""):
    try:
        result = supabase.table("meal_plans")\
            .select("plan_json, diet_pref")\
            .eq("id", plan_id)\
            .single()\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=404,
                detail="Plan not found"
            )

        plan_json = result.data["plan_json"]
        if isinstance(plan_json, str):
            import json
            plan_json = json.loads(plan_json)

        # Pull diet: query param > DB row > plan_json > default
        from services.diet_filter import DIET_VEGETARIAN
        diet_pref = (
            diet_pref
            or result.data.get("diet_pref")
            or plan_json.get("diet_pref")
            or DIET_VEGETARIAN
        ).lower().strip()

        gaps = calculate_nutrition_gap(plan_json, age_group, diet_pref)
        return {"gaps": gaps, "age_group": age_group}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=safe_error_detail(e))


@router.get("/food-equivalents")
async def food_equivalents(age_group: str = "9-12", diet_pref: str = "vegetarian"):
    """Practical food serving examples for nutrient targets, filtered by diet."""
    from services.diet_filter import DIET_VEGETARIAN
    safe_diet = (diet_pref or DIET_VEGETARIAN).lower().strip()
    return {"equivalents": get_food_equivalents(age_group, safe_diet), "age_group": age_group}


# ── Dashboard Stats ───────────────────────────────────────
@router.get("/dashboard/stats")
async def dashboard_stats(teacher_id: str, request: Request):
    try:
        await require_teacher_access(request, teacher_id)
        teacher = supabase.table("teachers")\
            .select("name, school_name")\
            .eq("id", teacher_id)\
            .single()\
            .execute()

        students = supabase.table("students")\
            .select("id", count="exact")\
            .eq("teacher_id", teacher_id)\
            .execute()

        plans = supabase.table("meal_plans")\
            .select("id", count="exact")\
            .eq("teacher_id", teacher_id)\
            .execute()

        month_start = datetime.now().strftime("%Y-%m-01")
        plans_month = supabase.table("meal_plans")\
            .select("id", count="exact")\
            .eq("teacher_id", teacher_id)\
            .gte("created_at", month_start)\
            .execute()

        assessments = supabase.table("bmi_records")\
            .select("id", count="exact")\
            .eq("teacher_id", teacher_id)\
            .execute()

        records = supabase.table("bmi_records")\
            .select("classification")\
            .eq("teacher_id", teacher_id)\
            .execute()

        dist = {}
        for r in records.data:
            c = r["classification"]
            dist[c] = dist.get(c, 0) + 1

        bmi_dist = [
            {"classification": k, "count": v}
            for k, v in dist.items()
        ]

        t = teacher.data or {}
        return {
            "teacher_name"     : t.get("name", ""),
            "school_name"      : t.get("school_name", ""),
            "total_students"   : students.count   or 0,
            "total_plans"      : plans.count      or 0,
            "plans_this_month" : plans_month.count or 0,
            "total_assessments": assessments.count or 0,
            "bmi_distribution" : bmi_dist,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=safe_error_detail(e))


# ── Dashboard Students ────────────────────────────────────
@router.get("/dashboard/students")
async def dashboard_students(teacher_id: str, request: Request):
    try:
        await require_teacher_access(request, teacher_id)
        students = supabase.table("students")\
            .select("*")\
            .eq("teacher_id", teacher_id)\
            .eq("is_active", True)\
            .execute()

        # Fetch all bmi_records for this teacher's students in one query,
        # ordered so the most-recent record for each student comes first.
        student_ids = [s["id"] for s in students.data]
        all_records = []
        if student_ids:
            all_records = supabase.table("bmi_records")\
                .select("student_id, bmi_value, classification, assessed_at")\
                .in_("student_id", student_ids)\
                .order("assessed_at", desc=True)\
                .execute().data

        # Keep only the first (latest) record seen per student.
        latest_map: dict = {}
        for rec in all_records:
            sid = rec["student_id"]
            if sid not in latest_map:
                latest_map[sid] = rec

        result = []
        for s in students.data:
            rec = latest_map.get(s["id"], {})
            result.append({
                "id"            : s["id"],
                "name"          : s["name"],
                "age"           : s["age"],
                "gender"        : s["gender"],
                "last_bmi"      : rec.get("bmi_value"),
                "classification": rec.get("classification"),
                "last_assessed" : rec.get("assessed_at", "")[:10]
                                  if rec else None,
            })

        return {"students": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=safe_error_detail(e))


# ── Recent Plans ──────────────────────────────────────────
@router.get("/dashboard/recent-plans")
async def recent_plans(teacher_id: str, request: Request):
    try:
        await require_teacher_access(request, teacher_id)
        plans = supabase.table("meal_plans")\
            .select(
                "student_name, share_token, "
                "region, diet_pref, month"
            )\
            .eq("teacher_id", teacher_id)\
            .order("created_at", desc=True)\
            .limit(5)\
            .execute()
        return {"plans": plans.data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=safe_error_detail(e))


# ── Class Progress ────────────────────────────────────────
@router.get("/class-progress")
async def class_progress(teacher_id: str, request: Request):
    try:
        await require_teacher_access(request, teacher_id)
        students = supabase.table("students")\
            .select("id, name, age, gender")\
            .eq("teacher_id", teacher_id)\
            .eq("is_active", True)\
            .execute()

        if not students.data:
            return {
                "error"         : "No students found",
                "total_students": 0,
            }

        records = supabase.table("bmi_records")\
            .select(
                "student_id, bmi_value, "
                "classification, percentile, assessed_at"
            )\
            .eq("teacher_id", teacher_id)\
            .order("assessed_at", desc=True)\
            .execute()

        # Latest record per student only
        seen   = set()
        latest = []
        for r in records.data:
            sid = r["student_id"]
            if sid not in seen:
                seen.add(sid)
                latest.append(r)

        dist = {
            "underweight": 0,
            "normal"     : 0,
            "overweight" : 0,
            "obese"      : 0,
        }
        total_percentile = 0
        assessed_count   = 0

        for r in latest:
            c = r["classification"]
            if c in dist:
                dist[c] += 1
            total_percentile += r.get("percentile", 50)
            assessed_count   += 1

        total_students = len(students.data)

        normal_pct   = (
            dist["normal"] / assessed_count * 100
        ) if assessed_count else 0
        health_score = round(normal_pct / 10, 1)

        avg_percentile = round(
            total_percentile / assessed_count, 1
        ) if assessed_count else 0

        if dist["underweight"] >= dist["overweight"]:
            deficiency = "Iron & Calories 🩸🔥"
            rec_en = "Add Ragi Mudde + Horsegram Saaru to daily lunch."
            rec_kn = "ದಿನದ ಊಟಕ್ಕೆ ರಾಗಿ ಮುದ್ದೆ + ಹುರಳಿ ಸಾರು ಸೇರಿಸಿ."
        else:
            deficiency = "Fiber & Vegetables 🥬"
            rec_en = "Replace fried snacks with seasonal vegetables."
            rec_kn = "ಕರಿದ ತಿಂಡಿ ಬದಲು ತರಕಾರಿ ನೀಡಿ."

        student_map = {s["id"]: s for s in students.data}
        leaderboard = []

        for r in latest:
            s = student_map.get(r["student_id"], {})
            dist_from_normal = abs(
                r.get("percentile", 50) - 50
            )
            leaderboard.append({
                "name"          : s.get("name", "Unknown"),
                "bmi"           : r["bmi_value"],
                "classification": r["classification"],
                "percentile"    : r.get("percentile", 50),
                "health_rank"   : dist_from_normal,
            })

        leaderboard.sort(key=lambda x: x["health_rank"])

        assessed_ids = {r["student_id"] for r in latest}
        not_assessed = [
            s for s in students.data
            if s["id"] not in assessed_ids
        ]

        return {
            "total_students"    : total_students,
            "assessed_count"    : assessed_count,
            "not_assessed"      : len(not_assessed),
            "not_assessed_names": [
                s["name"] for s in not_assessed[:5]
            ],
            "distribution"      : dist,
            "health_score"      : health_score,
            "karnataka_avg"     : 5.8,
            "avg_percentile"    : avg_percentile,
            "deficiency"        : deficiency,
            "recommendation"    : {
                "en": rec_en,
                "kn": rec_kn,
            },
            "top_5"             : leaderboard[:5],
            "needs_attention"   : leaderboard[-5:],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=safe_error_detail(e))