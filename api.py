import collections
from bson import ObjectId
import uvicorn
from fastapi import FastAPI, Query
import pandas as pd
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient


client = MongoClient("mongodb://localhost:27017")
db = client["llm_chatbot"]
collection = db["rankings"]


app = FastAPI()
class FeedbackEntry(BaseModel):
    serial_number: int
    selected_passage_ids: List[int]
    generated_answer_feedback: str
    remark: str
    email_address: str


@app.get("/")
async def read_data(serial_number: int=Query(..., description="The serial number to filter data")):
    df = pd.read_excel('./EvaluationDataset.xlsx')
    data = df[df['Serial Number'] == serial_number]
    result = data.to_dict('records')
    return result


@app.post("/feedback")
def submit_feedback(feedback: FeedbackEntry):
    print("here")
    feedback_dict = feedback.dict()
    import datetime
    feedback_dict["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    # feedback_dict["_id"] = ObjectId()
    # Save the feedback to MongoDB 
    insert_result = collection.insert_one(feedback_dict)

    # Print the inserted document's _id
    print("Inserted document ID:", insert_result.inserted_id)
    # collections.insert_one(feedback_dict)
    return {"message": f"Feedback submitted successfully {insert_result.inserted_id}"}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=9800)
