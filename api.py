import collections
from bson import ObjectId
import uvicorn
from fastapi import FastAPI, Query
import pandas as pd
from pydantic import BaseModel

app = FastAPI()
class FeedbackEntry(BaseModel):
    serial_number: int
    passage_rank: int
    generated_answer_feedback: str
    remark: str


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
    feedback_dict["_id"] = ObjectId()
    # Save the feedback to MongoDB 
    collections.insert_one(feedback_dict)
    return {"message": "Feedback submitted successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)