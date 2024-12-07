model link:`https://drive.google.com/file/d/1E2an9v6qZasbzoyugOOrr1wPEewa7FGf/view?usp=drive_link`。

操作說明:

1.安裝依賴: `pip install -r requirements.txt`。

2.到model link下載pm25_model.pth，並放在與api_air_prediction.py相同的位置。

3.執行`nohup python3 -m uvicion api_air_prediction:app --host 0.0.0.0 --port 33625 | tee fastapi.log &`。

檔案說明:

1.pm25_model.pth: 模型檔案。

2.test_module.py: 使用模型預測圖片。

3.api_air_prediction.py: 定期到環境部網站進行爬蟲，並將抓下來的資料使用test_module.py進行預測。

api說明:

1.local_host/metrics: 提供給prometheus所需資料。

2.local_host/download_and_predict?station=42: 包含當前預測的時間、預測的值、經緯度的資料，也有立即刷新資料的用處。

3.local_host/get_image: 目前預測的圖片。

其它:

1.可以到fastapi.log查詢之前執行的狀況。

2.api為後台運作，如果要取消執行，可以輸入指令`ps aux | grep uvicorn`找到對應的pid並執行kill。

3.環境部的資料大致為hour:06 ~ hour:08的時候更新，因此在hour:00時，圖片與預測資料大概不會更新。

4.剛啟動時可以call api說明中的2.來手動刷新資料，但若啟動時在hour:00 ~ hour:08，可能沒有資料。

5.若要新增其他測站，可以到config.json的"air_quality_station_prediction"，將這個list新增一個元素，並按照前面的格式輸入，最後將index改到新增的list index。

6.若只要找一個測站的資訊，可以修改"air_quality_station_prediction"[0]的內容就好。
