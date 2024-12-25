from machine import I2C, Pin
import time
from imu import MPU6050
import requests

# 初始化 I2C 和 MPU6050
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
imu = MPU6050(i2c)

# 設定地震偵測參數
THRESHOLD = 1.0  # 加速度閾值（單位 g）
INTERVAL = 0.5   # 每次讀取的時間間隔（秒）
CONSECUTIVE_COUNT = 3  # 持續超過閾值的次數判定地震
consecutive_count = 0

# Discord Webhook URL
webhook_url = "https://discord.com/api/webhooks/1320714925114396763/g7qXTkXqg5Tr8lbDKCg9QJtBesf1w4nWQ_CxtKxd2SALH-4s_stgiZslxeVDRu0UWiO0"

# 定義發送警報訊息到 Discord
def notify_alert(message, webhook_url):
    payload = {"content": "earthquake occurrence!"}
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 204:
            print("成功發送通知到 Discord。")
        else:
            print(f"發送通知失敗，狀態碼：{response.status_code}")
    except Exception as e:
        print(f"發送通知時出現錯誤: {e}")

# 用來標記是否已經發送過地震通知
earthquake_detected = False

# 無限循環
while True:
    try:
        # 讀取加速度數據
        ax = imu.accel.x
        ay = imu.accel.y
        az = imu.accel.z

        # 計算總加速度（不考慮方向）
        total_acceleration = (ax**2 + ay**2 + az**2)**0.5

        # 偵測地震
        if total_acceleration > THRESHOLD:
            consecutive_count += 1
            if consecutive_count >= CONSECUTIVE_COUNT and not earthquake_detected:
                print("⚠️ 確認地震發生！")
                # 發送警報訊息到 Discord
                alert_message = f"⚠️ 確認地震發生！\n總加速度: {total_acceleration:.2f} g"
                notify_alert(alert_message, webhook_url)
                earthquake_detected = True  # 設置標誌為已偵測到地震
                
                led = Pin(3,Pin.OUT)
                led.value(1)
                time.sleep(1)
                led.value(0)
    
                print("啟動蜂鳴器！")
                buzzer_pin = Pin(0, Pin.OUT)
                buzzer_pin.value(0)
                buzzer_pin.value(1)
                time.sleep(1)
                buzzer_pin.value(0)
        else:
            consecutive_count = 0  # 若未超過閾值，重置計數

        # 顯示加速度、陀螺儀數據與溫度
        gx = imu.gyro.x
        gy = imu.gyro.y
        gz = imu.gyro.z
        tem = round(imu.temperature, 2)
        print(f"ax: {ax:.2f} g, ay: {ay:.2f} g, az: {az:.2f} g")
        print(f"gx: {gx:.2f} °/s, gy: {gy:.2f} °/s, gz: {gz:.2f} °/s")
        print(f"Temperature: {tem:.2f} °C")
        print(f"總加速度: {total_acceleration:.2f} g\n")

        # 等待指定間隔
        time.sleep(INTERVAL)

        # 如果加速度小於閾值，重置地震檢測標誌
        if total_acceleration <= THRESHOLD and earthquake_detected:
            earthquake_detected = False
            
    except KeyboardInterrupt:
        print("程式中斷，關閉蜂鳴器。")
        break

    except Exception as e:
        print("讀取數據時出錯：", e)


