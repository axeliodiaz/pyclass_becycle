from fastapi import FastAPI

import settings
from single_version import get_schedules

app = FastAPI()

import asyncio


@app.get("/")
async def root():
    starting_class_id = settings.SCHEDULE_ID_START
    asyncio.create_task(get_schedules(starting_class_id))
    message = f"Checking classes from {settings.SCHEDULE_ID_START} class ID"
    return {"mensaje": message}
