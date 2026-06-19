from fastapi import FastAPI
import joblib
import numpy as np
from pydantic import BaseModel


app = FastAPI()

model = joblib.load('intrusion_model.pkl')
le_proto = joblib.load('protocol_type_encoder.pkl')
le_service = joblib.load('service_encoder.pkl')
le_flag = joblib.load('flag_encoder.pkl')   

class NetworkTrafficInput(BaseModel):
    duration: int
    protocol_type: str  
    service: str       
    flag: str           
    src_bytes: int
    dst_bytes: int
    logged_in: int
    count: int
    srv_count: int
    serror_rate: float
    rerror_rate: float
    dst_host_count: int
    dst_host_srv_count: int
    dst_host_diff_srv_rate: float

@app.get("/")
def home():
    return {
        "status": "healthy",
        "message": "Cyber Shield AI Backend is running smoothly!",
        "version": "1.0.0",
        "endpoints": {
            "prediction": "/predict",
            "interactive_docs": "/docs"
        }
    }
@app.post("/predict")
def predict(input_data: NetworkTrafficInput):
    try:
        # Encode categorical features using the loaded LabelEncoders
        protocol_type_encoded = le_proto.transform([input_data.protocol_type])[0]
        service_encoded = le_service.transform([input_data.service])[0]
        flag_encoded = le_flag.transform([input_data.flag])[0]

        # Prepare the input data for prediction
        input_array = np.array([
          input_data.duration,          # 1. duration
          protocol_type_encoded,          # 2. protocol_type
          service_encoded,        # 3. service
          flag_encoded,           # 4. flag
          input_data.src_bytes,         # 5. src_bytes
          input_data.dst_bytes,         # 6. dst_bytes
          0,                      # 7. land (Default 0)
          0,                      # 8. wrong_fragment (Default 0)
          0,                      # 9. urgent (Default 0)
          0,                      # 10. hot (Default 0)
          0,                      # 11. num_failed_logins (Default 0)
          input_data.logged_in,         # 12. logged_in
          0,                      # 13. num_compromised (Default 0)
          0,                      # 14. root_shell (Default 0)
          0,                      # 15. su_attempted (Default 0)
          0,                      # 16. num_root (Default 0)
          0,                      # 17. num_file_creations (Default 0)
          0,                      # 18. num_shells (Default 0)
          0,                      # 19. num_access_files (Default 0)
          0,                      # 20. num_outbound_cmds (Default 0)
          0,                      # 21. is_host_login (Default 0)
          0,                      # 22. is_guest_login (Default 0)
         input_data.count,             # 23. count
         input_data.srv_count,         # 24. srv_count
         input_data.serror_rate,       # 25. serror_rate
         0.0,                    # 26. srv_serror_rate (Default 0.0)
         input_data.rerror_rate,       # 27. rerror_rate
         0.0,                    # 28. srv_rerror_rate (Default 0.0)
         1.0,                    # 29. same_srv_rate (Default 1.0)
         0.0,                    # 30. diff_srv_rate (Default 0.0)
         0.0,                    # 31. srv_diff_host_rate (Default 0.0)
         input_data.dst_host_count,     # 32. dst_host_count
         input_data.dst_host_srv_count, # 33. dst_host_srv_count
         1.0,                    # 34. dst_host_same_srv_rate (Default 1.0)
         0.0,                    # 35. dst_host_diff_srv_rate (Yahan 0.0 kiya kyunki original column 35 par alag cheez hai)
         0.0,                    # 36. dst_host_same_src_port_rate (Default 0.0)
         input_data.dst_host_diff_srv_rate, # 37. dst_host_srv_diff_host_rate (Aapka input yahan map hoga NSL-KDD sequence ke mutabik)
         0.0,                    # 38. dst_host_serror_rate (Default 0.0)
         0.0,                    # 39. dst_host_srv_serror_rate (Default 0.0)
         0.0,                    # 40. dst_host_rerror_rate (Default 0.0)
         0.0                     # 41. dst_host_srv_rerror_rate (Default 0.0)
         ]).reshape(1, -1)

        # Make prediction using the loaded model
        prediction = model.predict(input_array)[0]
        probability = model.predict_proba(input_array)[0]

        if prediction == 1:
            result = "🔴 CYBER ATTACK DETECTED!"
            confidence = float(probability[1])
        else:
            result = "🟢 NORMAL TRAFFIC"
            confidence = float(probability[0])

        return {
              "status": "success",
              "prediction": int(prediction),              # Forcefully python standard int banaya
              "result": str(result),                      # String banaya
              "confidence_score": float(round(confidence * 100, 2))  # Forcefully python standard float banaya
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }