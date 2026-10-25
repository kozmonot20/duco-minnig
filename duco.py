import socket
import hashlib
import urllib.request
import json
import time

# --- KULLANICI AYARLARI ---
USERNAME = "KENDI_DUCO_KULLANICI_ADIN" # 1. Adımda açtığın kullanıcı adını buraya yaz!
MINER_NAME = "KozmoToaster"          # Canavarın adı :)

def get_mining_pool():
    """Duino-Coin sunucularından en uygun madencilik havuzunun IP ve Port bilgisini çeker."""
    try:
        # Havuz API'sine istek atıyoruz
        response = urllib.request.urlopen("https://duinocoin.com").read().decode()
        pool_data = json.loads(response)
        return pool_data["ip"], pool_data["port"]
    except Exception as e:
        print(f"❌ Havuz bilgisi alınamadı, tekrar deneniyor... Hata: {e}")
        time.sleep(5)
        return get_mining_pool()

def start_mining():
    print("🪐 Kozmonot20 Gerçek Kripto Madenciliği Başladı!")
    print(f"💻 Cihaz: {MINER_NAME} | 🎯 Hedef Cüzdan: {USERNAME}\n")
    
    while True:
        try:
            # 1. Havuz sunucusuna bağlan
            ip, port = get_mining_pool()
            print(f"🔗 Havuz sunucusuna bağlanılıyor: {ip}:{port}")
            
            soc = socket.socket()
            soc.connect((ip, int(port)))
            
            # Sunucu versiyon numarasını al (Bağlantı kontrolü)
            server_version = soc.recv(100).decode().rstrip("\n")
            print(f"🤖 Havuz Versiyonu: {server_version}")
            
            while True:
                # 2. Sunucudan madencilik görevi (Job) iste
                soc.send(f"JOB,{USERNAME},LOW,KozmoSecretKey".encode())
                job_data = soc.recv(1024).decode().rstrip("\n").split(",")
                
                # job_data içeriği: [önceki_blok_hash, hedef_hash, zorluk_derecesi]
                if len(job_data) < 3:
                    print("❌ Sunucudan geçersiz görev geldi, havuz yenileniyor...")
                    break
                    
                previous_hash = job_data[0]
                expected_hash = job_data[1]
                difficulty = int(job_data[2])
                
                start_time = time.time()
                
                # 3. DUCO-S1 Algoritması: Matematiksel bulmacayı çöz (Nonce Avı)
                # Önceki hash ile nonce sayısını birleştirip hedef hash'i yakalamaya çalışıyoruz
                for nonce in range(100 * difficulty + 1):
                    # SHA-1 şifreleme havuz kuralları gereğidir
                    hash_result = hashlib.sha1((previous_hash + str(nonce)).encode()).hexdigest()
                    
                    if hash_result == expected_hash:
                        end_time = time.time()
                        elapsed_time = end_time - start_time
                        hashrate = nonce / elapsed_time if elapsed_time > 0 else 0
                        
                        # 4. Bulunan sonucu (Nonce) havuz sunucusuna gönder
                        soc.send(f"{nonce},{hashrate:.0f},Python Minimal Miner,{MINER_NAME}".encode())
                        
                        # Sunucunun yanıtını al (GOOD = Kabul edildi, BAD = Reddedildi)
                        feedback = soc.recv(100).decode().rstrip("\n")
                        
                        if feedback == "GOOD":
                            print(f"🟢 Blok Kazıldı! Nonce: {nonce} | Hashrate: {hashrate/1000:.2f} kH/s | ⏱️ {elapsed_time:.3f}s -> Cüzdana Eklendi!")
                        else:
                            print(f"❌ Blok reddedildi: {feedback}")
                        break
                        
        except Exception as e:
            print(f"⚠️ Bağlantı koptu, 5 saniye sonra yeniden bağlanılıyor... Hata: {e}")
            time.sleep(5)

if __name__ == "__main__":
    start_mining()
