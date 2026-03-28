from fastapi import APIRouter, Form, File, UploadFile, HTTPException
from services.voice_analyze_service import process_audio_and_predict


router = APIRouter(
    prefix="/analyze",
    tags=["analyze"],
)

@router.post("/test")
async def test_endpoint(
    name: str = Form(...),
    age: int = Form(...),
    sex: str = Form(...),
    test_time: float = Form(...),
    audio_file: UploadFile = File(...)):

    
    return {
        "received_data": {
            "name": name,
            "age": age,
            "sex": sex,
            "test_time": test_time,
            "audio_file": {
                "filename": audio_file.filename,
                "content_type": audio_file.content_type,
                "size": len(await audio_file.read()) if audio_file else 0
            }
        },
        "status": "success"
    }

@router.post("/voice")
async def analyze_voice(
    name: str = Form(..., min_length=1, max_length=100),
    age: int = Form(..., gt=10, lt=120),
    sex: str = Form(..., pattern="^(male|female)$"),
    test_time: float = Form(..., gt=0),
    audio_file: UploadFile = File(...) ):

    # for debugging
    print("-" * 20)
    print("RECEIVED REQUEST FROM FRONTEND:")
    print(f" Name: {name}")
    print(f"Age: {age}")
    print(f"Sex: {sex}")
    print(f"Test Time: {test_time}")
    print(f"Audio File: {audio_file.filename} ")
    print(f"Audio Content Type: {audio_file.content_type}")
    
    # validation checks
    if not audio_file or audio_file.filename == "":
        print("---No audio file provided! ---")
        raise HTTPException(status_code=400, detail="No audio file provided")
    
    if audio_file.content_type and not audio_file.content_type.startswith(('audio/', 'application/octet-stream')):
        print(f"Unusual content type: {audio_file.content_type}")
    
    print("-" * 20)

    basic_info = {"age": age, "sex": sex, "name": name, "test_time": test_time}
    print(f"Basic info being passed to service: {basic_info}")
    
    try:
        result = await process_audio_and_predict(audio_file, basic_info)

        print("\nSENDING RESPONSE TO FRONTEND:")
        print(f"Response: {result}\n")
        return result
    except Exception as e:
        print("=" * 50)
        print("ERROR OCCURRED:")
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}\n")
        raise e