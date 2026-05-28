from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from riaes.database import get_db
from riaes.models.models import AgentTask, TaskStatus, Recommendation, Product

router = APIRouter()
templates = Jinja2Templates(directory="riaes/portal/templates")

@router.get("/", response_class=HTMLResponse)
async def portal_index(request: Request, db: Session = Depends(get_db)):
    tasks = db.query(AgentTask).order_by(AgentTask.created_at.desc()).all()
    active_agents = 9
    pending_approvals = db.query(AgentTask).filter(AgentTask.status == TaskStatus.PENDING).count()
    executed_decisions = db.query(AgentTask).filter(AgentTask.status == TaskStatus.EXECUTED).count()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "tasks": tasks,
            "active_agents": active_agents,
            "pending_approvals": pending_approvals,
            "executed_decisions": executed_decisions
        }
    )

@router.post("/task/{task_id}/approve")
async def approve_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(AgentTask).filter(AgentTask.id == task_id).first()
    if task:
        task.status = TaskStatus.EXECUTED
        db.commit()
    return RedirectResponse(url="/portal/", status_code=303)

@router.post("/task/{task_id}/reject")
async def reject_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(AgentTask).filter(AgentTask.id == task_id).first()
    if task:
        task.status = TaskStatus.REJECTED
        db.commit()
    return RedirectResponse(url="/portal/", status_code=303)
