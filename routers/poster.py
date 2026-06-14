from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from models.db import supabase
from models.schemas import MealPlan
from services.poster_context import build_poster_context
from routers.deps import safe_error_detail

import io
import json
import re
import qrcode
from urllib.parse import urlparse

router = APIRouter(tags=["Poster"])
templates = Jinja2Templates(directory="templates")


def _validate_qr_url(url: str, request: Request) -> str:
    """Only encode same-origin NutriPrint URLs to prevent open-redirect QR abuse."""
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise HTTPException(status_code=400, detail="Invalid URL")

    request_host = urlparse(str(request.base_url)).netloc.lower()
    if parsed.netloc.lower() != request_host:
        raise HTTPException(
            status_code=400,
            detail="URL must belong to this NutriPrint site",
        )

    return url.strip()


def _get_plan_by_token(token: str):
    result = (
        supabase.table("meal_plans")
        .select("*")
        .eq("share_token", token)
        .single()
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail="Plan not found"
        )

    row = result.data

    plan_json = row.get("plan_json", {})

    if isinstance(plan_json, str):
        plan_json = json.loads(plan_json)

    # Prevent duplicate keyword errors
    plan_json.pop("plan_id", None)
    plan_json.pop("share_token", None)

    plan_json["plan_id"] = str(row["id"])
    plan_json["share_token"] = str(row["share_token"])

    plan = MealPlan(**plan_json)

    return row, plan


@router.get("/plan/{share_token}", response_class=HTMLResponse)
async def plan_public(
    request: Request,
    share_token: str
):
    try:
        row, plan = _get_plan_by_token(share_token)

        base = str(request.base_url)
        if not base.endswith("/"):
            base += "/"

        ctx = build_poster_context(plan, share_token, base)
        ctx["request"] = request

        return templates.TemplateResponse(
            request=request,
            name="plan_public.html",
            context=ctx,
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=safe_error_detail(e)
        )

@router.get("/report/{share_token}", response_class=HTMLResponse)
async def health_report(
    request: Request,
    share_token: str
):
    try:
        row, plan = _get_plan_by_token(share_token)

        base = str(request.base_url)
        if not base.endswith("/"):
            base += "/"

        ctx = build_poster_context(plan, share_token, base)
        ctx["request"] = request

        return templates.TemplateResponse(
            request=request,
            name="health_report.html",
            context=ctx,
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=safe_error_detail(e)
        )


@router.get("/poster/{share_token}/print", response_class=HTMLResponse)
async def poster_print(
    request: Request,
    share_token: str,
):
    """Print-optimized HTML poster view."""
    try:
        row, plan = _get_plan_by_token(share_token)

        base = str(request.base_url)
        if not base.endswith("/"):
            base += "/"

        ctx = build_poster_context(plan, share_token, base)
        ctx["request"] = request

        return templates.TemplateResponse(
            request=request,
            name="poster_print.html",
            context=ctx,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=safe_error_detail(e))


@router.get("/api/plans/qr")
async def plan_qr(url: str, request: Request):
    """
    Generate a QR code PNG for the given URL.
    The URL to encode is passed as a query parameter:
        /api/plans/qr?url=https://...
    This avoids FastAPI path-parameter slash-splitting bugs that broke
    the previous  /api/plans/qr/{qr_code_string}  route.
    """
    if not url:
        raise HTTPException(status_code=400, detail="url parameter is required")

    url = _validate_qr_url(url, request)

    try:
        qr = qrcode.QRCode(
            version          = None,   # auto-size
            error_correction = qrcode.constants.ERROR_CORRECT_M,
            box_size         = 8,
            border           = 4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="image/png",
            headers={
                # Allow caching for 1 hour — QR for a given URL never changes
                "Cache-Control": "public, max-age=3600",
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=safe_error_detail(e))

@router.get("/poster/{share_token}/pdf")
async def download_pdf(
    share_token: str,
    request: Request
):
    try:
        from services.pdf_generator import generate_poster_pdf

        row, plan = _get_plan_by_token(share_token)

        try:
            plan_data = plan.model_dump()
        except AttributeError:
            plan_data = plan.dict()

        plan_data["share_token"] = share_token

        pdf_bytes = generate_poster_pdf(
            plan=plan_data,
            base_url=str(request.base_url),
        )

        safe_name = re.sub(
            r"[^a-zA-Z0-9_-]",
            "",
            plan.student_name.replace(" ", "_")
        )

        filename = f"NutriPrint_{safe_name}.pdf"

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition":
                f'attachment; filename="{filename}"'
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=safe_error_detail(e)
        )
