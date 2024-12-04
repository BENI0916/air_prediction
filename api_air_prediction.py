from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Gauge, generate_latest
from contextlib import asynccontextmanager
import os
import datetime
import requests
import test_module as tm  # 假設 test_module 中包含 predict_pm25 函數
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.responses import FileResponse
from fastapi.responses import Response
from fastapi.responses import PlainTextResponse
import json

CONFIG_FILE = "config.json"
app = FastAPI()
scheduler = BackgroundScheduler()

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)
ex_time_interval = config["crawler_time_interval_minutes"]
ex_index = config["index"]
ex_station_id = config["air_quality_station_prediction"][ex_index]["station_id"]
ex_latitude = config["air_quality_station_prediction"][ex_index]["location"]["latitude"]
ex_longitude = config["air_quality_station_prediction"][ex_index]["location"]["longitude"]

# Prometheus 指標
pm25_latest = Gauge("air_quality_prediction_pm25_microgram_cubic_meter", "Latest PM2.5 prediction value", ["latitude", "longitude", "station_id"])

# 全局變數存儲最新結果
latest_result = {}
old_img_url = None

def download_and_predict_task(station: int):
    """
    定時下載最新圖片並更新 PM2.5 預測結果。
    """
    global latest_result, old_img_url
    try:
        # 確保測站編號為 3 位數格式
        prefix = f"{station:03d}"
        
        # 獲取當前時間並向下取整至最近的整點
        current_time = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
        foldername = current_time.strftime('%Y%m%d')  # 生成當天的文件夾名稱 (格式: YYYYMMDD)
        
        # 構建圖片文件名和 URL
        filename = f"{prefix}-{current_time.strftime('%Y%m%d%H%M')}.jpg"
        folder_url = f"https://airtw.moenv.gov.tw/AirSitePic/{foldername}/"
        img_url = folder_url + filename
        
        local_path = 'predict_img.jpg'
        if old_img_url != img_url:
            img_response = requests.get(img_url)
            if img_response.status_code == 200:
                old_img_url = img_url
                with open(local_path, 'wb') as f:
                    f.write(img_response.content)
                print(f"Downloaded latest image: {filename}")
            else:
                print(f"No new image available yet. HTTP Status: {img_response.status_code}")
               # return
        
        # 使用模型預測 PM2.5 值
        pm25 = tm.predict_pm25(local_path, "pm25_model.pth")
        latest_result[station] = {
            "timestamp": current_time.isoformat(),
            "image_path": local_path,
            "pm25": pm25,
            "latitude": ex_latitude,
            "longitude": ex_longitude
        }
        
        # 更新 Prometheus 指標
        pm25_latest.labels( 
                latitude = ex_latitude,
                longitude = ex_longitude,
                station_id = ex_station_id
        ).set(pm25)
        print(filename)
        print(f"Prediction successful. PM2.5: {pm25}, Image Path: {local_path}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the image: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    使用 lifespan 初始化和關閉定時器。
    """
    print("Starting scheduler...")
    # 初始化定時器，定期更新數據
    station = 42  # 測站代碼
    scheduler.add_job(
        download_and_predict_task,
        'interval',
        minutes=ex_time_interval,
        args=[station],
        id="pm25_job"
    )
    scheduler.start()
    yield
    print("Shutting down scheduler...")
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {"message": "Welcome to the Air Photo & PM2.5 Prediction API"}

@app.get("/download_and_predict")
def get_latest_prediction(station: int):
    """
    返回最新的 PM2.5 預測結果。
    """
    if station in latest_result:
        return latest_result[station]
    else:
        download_and_predict_task(station)
        if station in latest_result:
            return latest_result[station]
    raise HTTPException(status_code=404, detail="No prediction data available yet.")

@app.get("/metrics", response_class = PlainTextResponse)
def metrics():
    """
    提供 Prometheus 格式的指標。
    """
    return generate_latest()

@app.get("/get_image")
def get_image():
    image_path = "predict_img.jpg"
    if not os.path.exists(image_path):
        raise HTTPException(status_code = 404, detail = "Image not found.")
    
    with open(image_path, "rb") as f:
        image_data = f.read()

    return Response(content = image_data, media_type = "image/jpeg")

# @app.get("/get_image")
# def get_image():
#    """
#    提供最新的圖片文件。
#    """
#    image_path = "predict_img.jpg"  # 圖片的存儲路徑
#    if not os.path.exists(image_path):
#        raise HTTPException(status_code=404, detail="Image not found.")
#    return FileResponse(image_path, media_type="image/jpeg", filename="predict_img.jpg")
