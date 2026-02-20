from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Task,User
from app.schemas import TaskCreate, TaskUpdate, TaskResponse
from app.depsjwt import get_current_user_from_cookies

router=APIRouter(prefix="/tasks",tags=["Tasks"])

@router.post("/",response_model=TaskResponse)
async def create_task(
        task: TaskCreate,
        db: AsyncSession=Depends(get_db),
        current_user: User= Depends(get_current_user_from_cookies)
):
    new_task=Task(title=task.title,
                  description=task.description,
                  owner_id=current_user.id)

    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task

@router.get("/",response_model=list[TaskResponse])
async def get_tasks(
        db: AsyncSession=Depends(get_db),
        current_user: User= Depends(get_current_user_from_cookies)
):
    if current_user.role=="Admin":
        result= await db.execute(select(Task))
    else:
        result= await  db.execute(select(Task).where(Task.owner_id==current_user.id))

    return result.scalars().all()

@router.put("/{task_id}",response_model=TaskResponse)
async def update_task(
        task_id: int,
        task_data: TaskUpdate,
        db: AsyncSession=Depends(get_db),
        current_user=Depends(get_current_user_from_cookies)
):
    result=await db.execute(select(Task).where(Task.id==task_id))
    task= result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404,detail="Task Not Found")
    if task.owner_id != current_user.id and current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Not Allowed")

    for field, value in task_data.dict(exclude_unset=True).items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return task

@router.delete("/{task_id}")
async def delete_task(
        task_id: int,
        db: AsyncSession=Depends(get_db),
        current_user: User=Depends(get_current_user_from_cookies)
):
    result=await db.execute(select(Task).where(Task.id==task_id))
    task=result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Not Found")
    if task.owner_id != current_user.id and current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Not Allowed")

    await db.delete(task)
    await db.commit()
    return {'Message :':f"Task ID - {task_id} has successfully Deleted"}



