import torch
import torch.nn as nn
from torchvision import models, transforms
from torchvision.models import ResNet18_Weights
from PIL import Image
import os

# 定義模型類別
class PM25Predictor(nn.Module):
    def __init__(self):
        super(PM25Predictor, self).__init__()
        self.model = models.resnet18(weights=ResNet18_Weights.DEFAULT)  # 預訓練 ResNet18
        self.model.fc = nn.Linear(self.model.fc.in_features, 1)  # 修改輸出層為單輸出

    def forward(self, x):
        return self.model(x)

# 定義圖片轉換
transform = transforms.Compose([
    transforms.Resize((224, 224)),  # 調整圖片大小
    transforms.ToTensor(),  # 轉為 Tensor
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # 正規化
])

# 定義推論函數 根據image path抓取圖片
def predict_pm25(image_path, model_path="pm25_model.pth", device=None):
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 加載模型
    model = PM25Predictor()
    model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True)["model_state_dict"])
    model = model.to(device)
    model.eval()

    # 加載圖片
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file {image_path} not found.")
    
    image = Image.open(image_path).convert('RGB')
    image = transform(image).unsqueeze(0)  # 增加批次維度
    image = image.to(device)

    # 推論
    with torch.no_grad():
        output = model(image).item()  # 獲取預測值
    
    return output

# 測試推論
if __name__ == "__main__":
    # 替換為您本地圖片的路徑和模型的路徑
    cnt = 0
    for hour in range(0, 24):
        test_image_path = f"test_images6/042-20241105{hour:0>2}00.jpg"
        model_path = "pm25_model.pth"

        try:
            pm25_value = predict_pm25(test_image_path, model_path)
            print(cnt, f"Predicted PM2.5 value: {pm25_value:.2f}")
        except Exception as e:
            print(f"Error: {e}")
        cnt += 1
