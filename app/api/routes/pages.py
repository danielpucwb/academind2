from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session
from starlette.templating import Jinja2Templates

from app.core.db import get_session
from app.core.paths import PROJECT_ROOT
from app.exceptions import (
    DomainConflictError,
    MergeLockBusyError,
    NotFoundError,
    NothingToMergeError,
    PdfMergeRejectedError,
)
from app.models.hierarchy import Course, Discipline
from app.repositories.catalogue import list_for_discipline
from app.services.artefact_service import delete_artefact_for_discipline
from app.services.hierarchy_service import HierarchyService
from app.services.ingestion_service import IngestionService
from app.services.pdf_merge_service import PdfMergeService
from app.services.processados_lock import MergeLock
from app.services.upload_batch_service import run_upload_burst

router = APIRouter(tags=["ui"])

TEMPLATE_DIR = PROJECT_ROOT / "app" / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


def get_service(request: Request, session: Annotated[Session, Depends(get_session)]) -> HierarchyService:
    return HierarchyService(session, request.app.state.settings)


ServiceDep = Annotated[HierarchyService, Depends(get_service)]


def _course_and_discipline_or_404(
    course_id: UUID, discipline_id: UUID, svc: HierarchyService
) -> tuple[Course, Discipline]:
    """Return relational course + discipline or raise FastAPI HTTP 404."""
    try:
        course = svc.get_course_or_raise(course_id)
        disc_rows = svc.list_disciplines_models(course_id)
        disc = next((d for d in disc_rows if d.id == discipline_id), None)
    except NotFoundError:
        raise HTTPException(status_code=404) from None
    if disc is None:
        raise HTTPException(status_code=404)
    return course, disc


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, svc: ServiceDep) -> HTMLResponse:
    courses = svc.list_courses_models()
    return templates.TemplateResponse(request, "dashboard.html", {"courses": courses, "error": None})


@router.post("/ui/cursos", response_class=HTMLResponse)
def ui_create_course(
    request: Request,
    nome: Annotated[str, Form()],
    svc: ServiceDep,
) -> HTMLResponse:
    nome = nome.strip()
    error: str | None = None
    try:
        if not nome:
            raise DomainConflictError("Nome obrigatório.")
        svc.create_course(nome)
    except DomainConflictError as exc:
        error = str(exc)

    hx = request.headers.get("HX-Request")
    if error:
        if hx:
            return HTMLResponse(
                f'<p class="form-error">{error}</p>',
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        return templates.TemplateResponse(
            request,
            "dashboard.html",
            {"courses": svc.list_courses_models(), "error": error},
            status_code=status.HTTP_409_CONFLICT,
        )

    if hx:
        return templates.TemplateResponse(
            request,
            "partials/course_rows.html",
            {"courses": svc.list_courses_models()},
        )
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/ui/cursos/{course_id}/excluir", response_class=HTMLResponse)
def ui_delete_course(course_id: UUID, request: Request, svc: ServiceDep) -> HTMLResponse:
    try:
        svc.delete_course(course_id)
    except NotFoundError:
        raise HTTPException(status_code=404) from None

    hx = request.headers.get("HX-Request")
    if hx:
        return templates.TemplateResponse(
            request,
            "partials/course_rows.html",
            {"courses": svc.list_courses_models()},
        )
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/cursos/{course_id}", response_class=HTMLResponse)
def course_discipline_view(course_id: UUID, request: Request, svc: ServiceDep) -> HTMLResponse:
    try:
        course = svc.get_course_or_raise(course_id)
    except NotFoundError:
        raise HTTPException(status_code=404) from None
    discs = svc.list_disciplines_models(course_id)
    return templates.TemplateResponse(
        request,
        "discipline_list.html",
        {"course": course, "disciplinas": discs, "error": None},
    )


@router.post("/ui/disciplinas", response_class=HTMLResponse)
def ui_create_discipline(
    request: Request,
    nome: Annotated[str, Form()],
    curso_id: Annotated[UUID, Form()],
    svc: ServiceDep,
) -> HTMLResponse:
    nome = nome.strip()
    try:
        course = svc.get_course_or_raise(curso_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    error: str | None = None
    try:
        if not nome:
            raise DomainConflictError("Nome obrigatório.")
        svc.create_discipline(curso_id, nome)
    except DomainConflictError as exc:
        error = str(exc)

    discs = svc.list_disciplines_models(curso_id)
    hx = request.headers.get("HX-Request")
    if error:
        if hx:
            return HTMLResponse(
                f'<p class="form-error">{error}</p>',
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        return templates.TemplateResponse(
            request,
            "discipline_list.html",
            {"course": course, "disciplinas": discs, "error": error},
            status_code=status.HTTP_409_CONFLICT,
        )

    if hx:
        return templates.TemplateResponse(
            request,
            "partials/discipline_rows.html",
            {"course": course, "disciplinas": discs},
        )
    return RedirectResponse(f"/cursos/{curso_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/cursos/{course_id}/disciplinas/{discipline_id}", response_class=HTMLResponse)
def discipline_detail(course_id: UUID, discipline_id: UUID, request: Request, svc: ServiceDep) -> HTMLResponse:
    course, disc = _course_and_discipline_or_404(course_id, discipline_id, svc)
    return templates.TemplateResponse(
        request,
        "discipline.html",
        {"course": course, "disciplina": disc},
    )


@router.get(
    "/ui/cursos/{course_id}/disciplinas/{discipline_id}/painel/originais",
    response_class=HTMLResponse,
)
def painel_originais(course_id: UUID, discipline_id: UUID, request: Request, svc: ServiceDep) -> HTMLResponse:
    course, disc = _course_and_discipline_or_404(course_id, discipline_id, svc)
    return templates.TemplateResponse(
        request,
        "partials/originais_panel.html",
        {"course": course, "disciplina": disc},
    )


@router.get(
    "/ui/cursos/{course_id}/disciplinas/{discipline_id}/painel/processados",
    response_class=HTMLResponse,
)
def painel_processados(course_id: UUID, discipline_id: UUID, request: Request, svc: ServiceDep) -> HTMLResponse:
    course, disc = _course_and_discipline_or_404(course_id, discipline_id, svc)
    return templates.TemplateResponse(
        request,
        "partials/processados_panel.html",
        {"course": course, "disciplina": disc},
    )


@router.get(
    "/ui/cursos/{course_id}/disciplinas/{discipline_id}/originals-rows",
    response_class=HTMLResponse,
)
def originals_rows(
    course_id: UUID,
    discipline_id: UUID,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
) -> HTMLResponse:
    svc = HierarchyService(session, request.app.state.settings)
    course, disc = _course_and_discipline_or_404(course_id, discipline_id, svc)
    artefacts = list_for_discipline(session, discipline_id)
    return templates.TemplateResponse(
        request,
        "partials/originals_list.html",
        {"course": course, "disciplina": disc, "artefacts": artefacts},
    )


@router.post(
    "/ui/cursos/{course_id}/disciplinas/{discipline_id}/artefact-excluir",
    response_class=HTMLResponse,
)
def artefact_excluir_htmx(
    course_id: UUID,
    discipline_id: UUID,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    curso_id: Annotated[UUID, Form()],
    artefact_id: Annotated[UUID, Form()],
) -> HTMLResponse:
    svc = HierarchyService(session, request.app.state.settings)
    _course_and_discipline_or_404(curso_id, discipline_id, svc)
    if curso_id != course_id:
        raise HTTPException(status_code=400, detail="curso inconsistente.") from None
    try:
        delete_artefact_for_discipline(session, request.app.state.settings, discipline_id, artefact_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Artefact não encontrado.") from None

    refreshed_course, refreshed_disc = _course_and_discipline_or_404(curso_id, discipline_id, svc)
    artefacts = list_for_discipline(session, discipline_id)
    return templates.TemplateResponse(
        request,
        "partials/originals_list.html",
        {"course": refreshed_course, "disciplina": refreshed_disc, "artefacts": artefacts},
    )


@router.post(
    "/ui/cursos/{course_id}/disciplinas/{discipline_id}/upload-htmx",
    response_class=HTMLResponse,
)
async def originals_upload_htmx(
    course_id: UUID,
    discipline_id: UUID,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    curso_id: Annotated[UUID, Form()],
    files: Annotated[list[UploadFile], File()],
) -> HTMLResponse:
    svc = HierarchyService(session, request.app.state.settings)
    _course_and_discipline_or_404(curso_id, discipline_id, svc)
    if curso_id != course_id:
        raise HTTPException(status_code=400, detail="curso inconsistente.") from None

    if not files:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Seleccione pelo menos um ficheiro.")

    course, disc = _course_and_discipline_or_404(curso_id, discipline_id, svc)
    ing = IngestionService(session, request.app.state.settings)

    try:
        bundle = await run_upload_burst(ing, discipline_id, files)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada.") from None

    artefacts = list_for_discipline(session, discipline_id)

    def oob_resp(lines: list[str], *, success: bool, error: bool) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            "partials/htmx_upload_oob.html",
            {
                "course": course,
                "disciplina": disc,
                "artefacts": artefacts,
                "alert_lines": lines,
                "alerts_success": success,
                "alerts_error": error,
            },
        )

    homogeneous_tl = bundle.too_large and not bundle.created and not bundle.duplicates and not bundle.rejected
    homogeneous_rej = bundle.rejected and not bundle.created and not bundle.duplicates and not bundle.too_large
    homogeneous_dup = bundle.duplicates and not bundle.created and not bundle.rejected and not bundle.too_large

    if homogeneous_tl:
        msgs = [x["detail"] for x in bundle.too_large]
        return oob_resp(msgs or ["Pedido demasiado grande."], success=False, error=True)
    if homogeneous_rej:
        return oob_resp(
            [f'{r["filename"]}: {r["detail"]}' for r in bundle.rejected],
            success=False,
            error=True,
        )
    if homogeneous_dup:
        return oob_resp(
            [f'{d["filename"]}: {d["detail"]}' for d in bundle.duplicates],
            success=False,
            error=True,
        )

    lines: list[str] = []
    any_problem = False
    if bundle.created:
        lines.append(f"Ingestão concluída: {len(bundle.created)} ficheiro(s) registados.")
    for bucket, title in (
        (bundle.duplicates, "Duplicados"),
        (bundle.rejected, "Rejeitados"),
        (bundle.too_large, "Demasiado grandes"),
    ):
        if not bucket:
            continue
        any_problem = True
        preview = "; ".join(f'{x["filename"]}' for x in bucket[:3])
        lines.append(f"{title}: {preview}")

    if not lines:
        lines.append("Sem alterações registadas.")

    return oob_resp(
        lines,
        success=bool(bundle.created) and not any_problem,
        error=any_problem,
    )


@router.post("/ui/disciplinas/{discipline_id}/merge-pdfs", response_class=HTMLResponse)
async def merge_pdfs_htmx(
    discipline_id: UUID,
    request: Request,
    curso_id: Annotated[UUID, Form()],
    session: Annotated[Session, Depends(get_session)],
) -> HTMLResponse:
    svc = HierarchyService(session, request.app.state.settings)
    _course_and_discipline_or_404(curso_id, discipline_id, svc)

    lock = getattr(request.app.state, "pdf_merge_lock", None) or MergeLock()
    merger = PdfMergeService(session, request.app.state.settings, merge_lock=lock)

    messages: list[str]
    diag_ctx: list[dict[str, object]] = []

    try:
        out = await merger.merge_discipline_pdf(discipline_id)
    except MergeLockBusyError as exc:
        messages = [str(exc)]
        return templates.TemplateResponse(
            request,
            "partials/merge_feedback.html",
            {"level": "error", "messages": messages, "diags": diag_ctx},
        )
    except NothingToMergeError as exc:
        messages = [str(exc)]
        return templates.TemplateResponse(
            request,
            "partials/merge_feedback.html",
            {"level": "warning", "messages": messages, "diags": diag_ctx},
        )
    except PdfMergeRejectedError as exc:
        messages = [exc.reason_pt]
        diag_ctx = list(exc.diagnostics)
        return templates.TemplateResponse(
            request,
            "partials/merge_feedback.html",
            {"level": "error", "messages": messages, "diags": diag_ctx},
        )
    except NotFoundError:
        raise HTTPException(status_code=404) from None

    diag_ctx = [d.as_dict() for d in out.diagnostics]
    messages = [
        f"Ficheiro concatenado atualizado com sucesso ({out.page_count} páginas ao todo). "
        "As transcritas Faster‑Whisper surgirão neste separador quando o pipeline multimédia estiver ativo."
    ]
    return templates.TemplateResponse(
        request,
        "partials/merge_feedback.html",
        {"level": "success", "messages": messages, "diags": diag_ctx},
    )


@router.post("/ui/disciplinas/{discipline_id}/excluir", response_class=HTMLResponse)
def ui_delete_discipline(
    discipline_id: UUID,
    request: Request,
    curso_id: Annotated[UUID, Form()],
    svc: ServiceDep,
) -> HTMLResponse:
    try:
        svc.delete_discipline(discipline_id)
    except NotFoundError:
        raise HTTPException(status_code=404) from None

    course = svc.get_course_or_raise(curso_id)
    discs = svc.list_disciplines_models(curso_id)
    hx = request.headers.get("HX-Request")
    if hx:
        return templates.TemplateResponse(
            request,
            "partials/discipline_rows.html",
            {"course": course, "disciplinas": discs},
        )
    return RedirectResponse(f"/cursos/{curso_id}", status_code=status.HTTP_303_SEE_OTHER)
