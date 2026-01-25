#!/usr/bin/env python3
import serial
import time
import sys
import glob

# --- 設定項目 ---
APN = "soracom.io"
USER = "sora"
PASSWORD = "sora"
TARGET_PORT = "/dev/ttyUSB5"  # 今回特定されたポート

def find_at_port():
    """指定ポートが開けない場合、他のポートを探す"""
    print("指定ポートが見つからないため、利用可能なポートをスキャンします...")
    ports = glob.glob('/dev/ttyUSB*')
    for port in ports:
        try:
            ser = serial.Serial(port, 115200, timeout=1)
            ser.write(b"AT\r\n")
            resp = ser.read(100)
            ser.close()
            if b"OK" in resp:
                return port
        except:
            continue
    return None

def send_at(ser, cmd, wait=1, verbose=True):
    if verbose:
        print(f"[送信] {cmd}")
    ser.write((cmd + "\r\n").encode())
    time.sleep(wait)
    resp = ""
    while ser.in_waiting:
        try:
            resp += ser.read(ser.in_waiting).decode(errors='ignore')
        except:
            pass
    if verbose:
        print(f"[受信] {resp.strip()}")
    return resp

def setup_modem():
    port = TARGET_PORT
    
    print(f"ポート {port} に接続しています...")
    try:
        ser = serial.Serial(port, 115200, timeout=2)
    except Exception as e:
        print(f"エラー: {port} を開けませんでした。")
        port = find_at_port()
        if not port:
            print("ATコマンド対応のポートが見つかりませんでした。接続を確認してください。")
            return
        print(f"ポート {port} を発見しました。こちらを使用します。")
        ser = serial.Serial(port, 115200, timeout=2)

    ser.flushInput()
    send_at(ser, "ATE0") # エコーオフ

    print("\n=== 1. ネットワークモード設定 (LTE Only) ===")
    print("3G/GSMへの接続を防ぐため、LTE専用モードに設定します...")
    # nwscanmode: 3 = LTE Only (EG915U-LA用)
    resp = send_at(ser, 'AT+QCFG="nwscanmode",3')
    
    if "ERROR" in resp:
        print("警告: 設定コマンドがエラーになりました。代替コマンドを試します...")
        send_at(ser, 'AT+QCFG="nwscanmode",3,1')

    print("\n=== 2. APN設定 (SORACOM) ===")
    print(f"APNを {APN} に設定します...")
    # APNの設定 (CID 1)
    send_at(ser, f'AT+CGDCONT=1,"IP","{APN}"')
    
    # 認証情報の設定 (ユーザー名/パスワード/認証タイプ)
    # 3 = PAP/CHAP自動
    send_at(ser, f'AT+QICSGP=1,1,"{APN}","{USER}","{PASSWORD}",3')

    print("\n=== 3. 設定保存と再起動 ===")
    send_at(ser, "AT&W")        # 設定保存
    send_at(ser, "AT+CFUN=1,1") # モデム再起動
    ser.close()

    print("モデムを再起動しています... (20秒待機)")
    time.sleep(20)

    print("\n=== 4. 接続確認 ===")
    try:
        ser = serial.Serial(port, 115200, timeout=2)
        send_at(ser, "ATE0", verbose=False)
        
        # 接続待ちループ (最大60秒)
        for i in range(1, 13):
            print(f"\n[試行 {i}/12] 状態を確認中...")
            
            # SIM状態
            cpin = send_at(ser, "AT+CPIN?", verbose=False)
            if "READY" not in cpin:
                print("SIM準備中...")
                time.sleep(5)
                continue
                
            # 電波状態
            csq = send_at(ser, "AT+CSQ", verbose=False).strip()
            print(f"電波強度: {csq}")
            
            # 登録状態
            cereg = send_at(ser, "AT+CEREG?", verbose=False).strip()
            print(f"登録状態: {cereg}")
            
            # 0,1 (ホーム) または 0,5 (ローミング) なら成功
            if "+CEREG: 0,1" in cereg or "+CEREG: 0,5" in cereg:
                print("\n成功！ ネットワークに接続されました。")
                break
            
            # 0,0 (未検索) なら強制検索
            if "+CEREG: 0,0" in cereg:
                print("検索開始 (AT+COPS=0)...")
                send_at(ser, "AT+COPS=0", verbose=False)
            
            # 0,2 (検索中) なら待機
            elif "+CEREG: 0,2" in cereg:
                print("ネットワーク検索中...")
                
            time.sleep(5)
            
        # 最終ステータス表示
        print("\n=== 最終ステータス ===")
        # IPアドレス取得
        ip_resp = send_at(ser, "AT+CGPADDR=1")
        # 接続事業者
        ops_resp = send_at(ser, "AT+COPS?")
        
        if "+CGPADDR" in ip_resp and '0.0.0.0' not in ip_resp:
            print("\n*** 接続成功 ***")
            print("SORACOMによる通信が確立しています。")
        else:
            print("\nIPアドレスがまだ取得できていない可能性があります。")
            print("数分待ってから、SORACOMコンソールでオンライン状態を確認してください。")
        
        ser.close()
    except Exception as e:
        print(f"接続確認中にエラーが発生しました: {e}")

if __name__ == "__main__":
    setup_modem()
