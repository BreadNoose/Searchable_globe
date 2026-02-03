from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
import os

# 1. CONFIGURATION
# Replace these with your actual Supabase URL and Key
SUPABASE_URL = "https://jgevkzslmovbnwpdmogq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpnZXZrenNsbW92Ym53cGRtb2dxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk4MDU4NjUsImV4cCI6MjA4NTM4MTg2NX0.DRJMeCtcxrbKvY_pWpCIvJ0GP4WGXqP6cidj9nxFkog"

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize FastAPI
app = FastAPI()

# 2. ENABLE CORS (Allow your HTML file to talk to this Python server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (good for local dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. DEFINE DATA MODELS (What data do we expect?)
class Location(BaseModel):
    name: str
    lat: float
    lng: float
    color: str

# 4. API ROUTE: GET ALL PLACES
# --- UPDATE THIS FUNCTION ---
@app.get("/places")
def get_places(search: str = ""):
    # Start the query
    query = supabase.table("places_view").select("*")
    
    # If the user typed something, filter by name
    if search:
        query = query.ilike("name", f"%{search}%")
    
    # Execute and return
    response = query.execute()
    return response.data

# 5. API ROUTE: ADD NEW PLACE
@app.post("/places")
def add_place(location: Location):
    # Validation logic is now handled by Pydantic (above), but we can add more:
    if not location.name.strip():
        raise HTTPException(status_code=400, detail="Name cannot be empty")

    # Format for PostGIS
    point_string = f"POINT({location.lng} {location.lat})"

    data = {
        "name": location.name,
        "color": location.color,
        "location": point_string
    }

    try:
        response = supabase.table("places").insert(data).execute()
        return {"message": "Success", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 6. API ROUTE: DELETE PLACE
@app.delete("/places/{place_id}")
def delete_place(place_id: int):
    try:
        supabase.table("places").delete().eq("id", place_id).execute()
        return {"message": "Deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
