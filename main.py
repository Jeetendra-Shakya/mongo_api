from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client["euron"]
euron_data = db["euron_collection"]
app = FastAPI()

class eurondata(BaseModel):
    name: str
    phone: int
    city: str
    course: str

# Update model (all fields optional)
class eurondata_update(BaseModel):
    name: Optional[str] = None
    phone: Optional[int] = None
    city: Optional[str] = None
    course: Optional[str] = None
    
@app.post("/euron/insert")    
async def euron_data_insert_helper(data:eurondata):
    result  = await euron_data.insert_one(data.dict())
    return str(result.inserted_id)

def euron_helper(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

@app.get("/euron/showdata")
async def show_euron_data():
    iterms = []
    cursor = euron_data.find({})
    async for document in cursor:
        iterms.append(euron_helper(document))
    return iterms

@app.put("/euron/update/{id}")
async def update_euron_data(id: str, data: eurondata_update):
    update_fields = {k: v for k, v in data.dict().items() if v is not None}
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields provided to update.")
    result = await euron_data.update_one(
        {"_id": ObjectId(id)},
        {"$set": update_fields}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"msg": "Document updated successfully."}

@app.delete("/euron/delete/{id}")
async def delete_euron_data(id: str):
    result = await euron_data.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"msg": "Document deleted successfully."}