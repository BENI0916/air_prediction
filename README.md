model link:https://drive.google.com/file/d/1E2an9v6qZasbzoyugOOrr1wPEewa7FGf/view?usp=drive_link

操作說明:

1.安裝依賴: pip install -r requirements.txt

2.到model link下載pm25_model.pth，並放在與api_air_prediction.py相同的位置

3.執行nohup python3 -m uvicion api_air_prediction:app --host 0.0.0.0 --port 33625 | tee fastapi.log &

檔案說明:

1.pm25_model.pth: 模型檔案

2.test_module.py: 使用模型預測圖片

3.api_air_prediction.py: 定期到環境部網站進行爬蟲，並將抓下來的資料使用test_module.py進行預測。

api說明:

1.local_host/metrics: 提供給prometheus所需資料

2.local_host/download_and_predict?station=42: 包含當前預測的時間、預測的值、經緯度的資料。

3.local_host/get_image: 目前預測的圖片
