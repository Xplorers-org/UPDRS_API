import os
from utils.file_handler import save_temp_file
from ml.model_predictor import predict_parkinson
from utils.voice_data_extraction import extract_voice_features

async def process_audio_and_predict(audio_file, basic_info):
    print("PROCESSING IN SERVICE:")
    print(f"Received basic_info: {basic_info}")
    print(f"Audio file object: {type(audio_file)}")

    temp_file_path = await save_temp_file(audio_file)

    try:
        voice_features = extract_voice_features(temp_file_path)

        prediction_features = basic_info.copy()

        # Encode sex: male=1, female=0
        if 'sex' in prediction_features:
            prediction_features['sex'] = 1 if prediction_features['sex'].lower() == 'male' else 0

        feature_data = {**prediction_features, **voice_features}

        print("CALLING ML MODEL...")
        prediction = predict_parkinson(feature_data)

        final_result = {"prediction": prediction}
        print(f"FINAL RESULT: {final_result}")

        return final_result
    finally:
        # Always clean up the temp file from disk
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"Cleaned up temp file: {temp_file_path}")
