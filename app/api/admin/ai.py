from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.database.session import get_db
from app.dependencies.auth import get_current_admin
from app.models.ai_agent import AIGeneratedContent, AIResearchTask, ContentCalendar, SEOAudit
from app.models.auth import User
from app.schemas.common import success_response
from app.services.ai_research_agent import AIResearchAgent
from app.services.ai_seo_agent import AISEOAgent
from app.services.websocket import manager

router = APIRouter(prefix="/ai", tags=["Admin - AI Agents"])
research_agent = AIResearchAgent()
seo_agent = AISEOAgent()


class ResearchTopicRequest(BaseModel):
    topic: str
    niche: Optional[str] = "Personal Finance"


class ContentApprovalRequest(BaseModel):
    approved: bool
    feedback: Optional[str] = None


@router.post("/research/trigger")
async def trigger_research(
    request: ResearchTopicRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Admin triggers the agent to research a topic and generate a draft."""
    async def run_research_task():
        try:
            await manager.broadcast({"type": "ai_research", "status": "started", "message": f"Starting research on '{request.topic}'..."})
            # 1. Research
            research_result = await research_agent._deep_research(request.topic)
            task = AIResearchTask(
                topic=request.topic,
                keywords=research_result.get("keywords", []),
                results=research_result,
                status="completed",
            )
            db.add(task)
            db.commit()
            db.refresh(task)

            # 2. Generate Content
            draft_content = await research_agent._generate_blog_draft(
                topic=request.topic,
                research=research_result,
            )

            content = AIGeneratedContent(
                research_task_id=task.id,
                title=draft_content.get("title", f"The Ultimate Guide to {request.topic}"),
                content=draft_content.get("content", ""),
                meta_title=draft_content.get("meta_title"),
                meta_description=draft_content.get("meta_description"),
                status="draft",
            )
            db.add(content)
            db.commit()

            await manager.broadcast({"type": "ai_research", "status": "completed", "message": f"Research on '{request.topic}' completed successfully!"})

        except Exception as e:
            print(f"Research task failed: {e}")
            await manager.broadcast({"type": "ai_research", "status": "failed", "message": f"Research on '{request.topic}' failed: {e}"})

    background_tasks.add_task(run_research_task)
    return success_response(message="AI Research task started in background")


@router.get("/content/pending")
def get_pending_content(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Admin gets list of generated content pending approval."""
    contents = db.query(AIGeneratedContent).filter(AIGeneratedContent.status == "draft").all()
    return success_response(data=[{"id": c.id, "title": c.title, "content": c.content, "type": "blog_post", "created_at": c.created_at} for c in contents])


@router.post("/content/{content_id}/approve")
def approve_content(
    content_id: str,
    request: ContentApprovalRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    content = db.query(AIGeneratedContent).filter(AIGeneratedContent.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    calendar = db.query(ContentCalendar).filter(ContentCalendar.content_id == content.id).first()

    if request.approved:
        content.status = "published"
        if calendar:
            calendar.status = "published"
    else:
        content.status = "rejected"

    db.commit()
    return success_response(message=f"Content {'approved' if request.approved else 'rejected'}")


@router.post("/seo/audit")
async def trigger_seo_audit(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    async def run_seo_audit():
        try:
            await manager.broadcast({"type": "seo_audit", "status": "started", "message": "Starting SEO audit across site..."})
            pages = [
                {"url": "/calculators/mortgage", "title": "Mortgage Calculator", "content": "Calculate mortgage payments"},
                {"url": "/calculators/auto-loan", "title": "Auto Loan Calculator", "content": "Calculate auto loan payments"},
            ]
            audit_results = await seo_agent.audit_pages(pages)

            audit = SEOAudit(
                url="/all",
                issues=audit_results.get("page_results", []),
                score=audit_results.get("overall_score", 85),
                recommendations=audit_results.get("recommendations", []),
            )
            db.add(audit)
            db.commit()
            await manager.broadcast({"type": "seo_audit", "status": "completed", "message": "SEO audit completed successfully!"})
        except Exception as e:
            print(f"SEO audit background task failed: {e}")
            await manager.broadcast({"type": "seo_audit", "status": "failed", "message": f"SEO audit failed: {e}"})

    background_tasks.add_task(run_seo_audit)
    return success_response(message="SEO Audit started in background")


@router.get("/seo/audits")
def get_seo_audits(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Get list of past SEO audits."""
    audits = db.query(SEOAudit).order_by(SEOAudit.created_at.desc()).limit(20).all()
    # Format according to what the frontend expects
    results = []
    for a in audits:
        results.append({
            "id": a.id,
            "target_url": a.url,
            "score": a.score,
            "created_at": a.created_at.isoformat(),
            "recommendations": a.recommendations,
        })
    return success_response(data=results)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
