import requests
import json
import time

def get_gzctf_token():
    """
    登录系统获取GZCTF_Token Cookie，并保存到文件及显示在终端
    """
    # 登录API端点
    url = "http://192.168.247.134/api/account/login"
    
    # 请求头信息
    headers = {
        "Host": "192.168.247.134",
        "Content-Length": "47",
        "Accept-Language": "zh-CN",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Origin": "http://192.168.247.134",
        "Referer": "http://192.168.247.134/account/login?from=/",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    
    # 登录数据
    payload = {
        "userName": "Admin",
        "password": "Admin_123_nya"
    }
    
    try:
        # 发送POST请求
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
        
        # 检查响应状态
        if response.status_code == 200:
            # 从响应头中获取Cookie
            cookies = response.cookies
            
            # 查找GZCTF_Token
            gzctf_token = None
            for cookie in cookies:
                if cookie.name == "GZCTF_Token":
                    gzctf_token = cookie.value
                    break
            
            if gzctf_token:
                # 保存到文件
                with open("cookie.txt", "w") as f:
                    f.write(f"GZCTF_Token={gzctf_token}\n")
                print(f"成功获取GZCTF_Token，已保存到cookie.txt")
                
                # 在终端显示
                print("\n===== GZCTF_Token 信息 =====")
                print(f"名称: GZCTF_Token")
                print(f"值: {gzctf_token}")
                print(f"保存时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print("==========================\n")
            else:
                print("未找到GZCTF_Token Cookie")
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
    except Exception as e:
        print(f"发生错误: {e}")


def get_games(count=30, skip=0):
    """获取竞赛列表，返回id和title信息"""
    url = f"http://192.168.247.134/api/edit/games?count={count}&skip={skip}"
    headers = {
        "Accept-Language": "zh-CN",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Referer": "http://192.168.247.134/admin/games",
        "Cookie": "GZCTF_Token=CfDJ8Gu5Y0c4rA5FoOApV1A6BrSMG90s4czptKsFCK9Zs1PTWQw5Xxecj5JiPjus4H8gNSWgRLjPWT5psnu4ZlGxfje8QH5C466Mynu2UlOuNS3YrVyf0B_ZLe2-3-giiomkEunLjzjur3D0JxvTqKHuxvmr2lC40bQJy82N4v3D5Ukg6l9rn9h73jrb2zUgrQfsIxftNmgc_U3XSEDAdIWmUSQ-442whs6A2kMTEPuMuSKSpovyoCjabBmcTNoqHWNszu9jdIC2u3nhsp7rw4BlIyE1HZbseWRU8DmSt7PwiBB-q0Ei_gRnUOZa0o2plRMFV5QpG1kcmGNlukE-PjXrOuHIC6_VQqNkSC5uV80IvZnWKdCPbOwleSbFPi9Vh5PGwDsr6aC4ZmMXMt1zDVKlnPvatfX-VmUiPCwHEFBJXSoErIQDO82djxHbkcQfexPckEKk1YhVa4qn0cQylpQFOT6fLaYCRzKG-xSdoWJ0E73YQiqBEewcZVPawDBJDGyigEEw7jsVVRaYiMBPoZKwuVhlOl17mr2rFdzudiBbMTSl24_Yzfa-ZoyRRfdIawGknSQo2djRkDXR0id8ipZhkTt_7P2SabPTwtSlCCIGcYlGKqeF9xTWbtP1tsDtIKuD8AqCW8TfxTYq-4myHSW04z2-mIznE6Jc3SU9A1nEePyZNlfznPgeMFD-sPHWBlXLDfI2dRYlgwtgHcGCTQbgMs2Bh_z4Y1Ynl1wDHGbTUXxP"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        games = data.get("data", [])
        
        # 提取id和title
        result = []
        for game in games:
            result.append({
                "id": game.get("id"),
                "title": game.get("title")
            })
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"请求出错: {e}")
        return []
    except (KeyError, ValueError) as e:
        print(f"解析响应出错: {e}")
        return []


def create_game():
    """
    创建新赛事，运行时会提示用户输入赛事标题

    返回:
    dict: 包含赛事信息的字典，如果出错则返回None
    """
    url = "http://192.168.247.134/api/edit/games"
    
    # 设置请求头
    headers = {
        "Accept-Language": "zh-CN",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Origin": "http://192.168.247.134",
        "Referer": "http://192.168.247.134/admin/games",
        "Cookie": "GZCTF_Token=CfDJ8Gu5Y0c4rA5FoOApV1A6BrSJNOuUeyq2pRN9kdqkBzySaLcSAJJVkFaoDmokO4IC7FDZrPM6Dxrf8_K1AN7faR6kC5pvCQen_g6yusOxqdkWjpzmb09ZbRj0oz5S21uZ1MtebnvXEC17SMLfb89m-ytK9W4pmmK5uEUGucQaR3nfOEX3wkldnmVPlsxvltAQqGamOlPkkux39R45IEj-dXlMYJJsvxiaffzaf7KQwq76uE0msXaqd1HiFe3H5Gt7ZdVm5X2QEfC0To54HtkxwpqOCii-ZipNUjd10TEJo8ER6nkLgrKa8vIxqSGQ0mzerQ8QQwrxgXAugB_piyOIq2Y8SgUganSsEhTVtruRBTPaQSmOClNXLIRkcBs5m8j6ZVPXpFKX00UCwTuPTO-N7Au1QpXhDCgkQrYsJ5DtYym6xEf4BJDpQ_5d1kHfQCn0FKx0klHPJAWqPqXfR8o0LM1cFWSIGp03YCSLpnFAjs18R_PYqcbaiEuuOfeUqdzuhuNbzVCkGCGPSZUJxt_TYgBR62D0177oqWirj7Eu5P7_O37T8qMaowOUUMKhS20ER-NeNfVpgy_fALe0SzXAt-1wPkbOW3LUcCLldRXEYj1ndEZVGuvxMWObBofGJnDAAr4AqFUR5d8lsKriMU-B92OrYptkP-MwMrEcaVQVdTj3yR6KrdEKQK_XGXFUiiJX9hQqTGTt6_q-6CmjeusFeRo"
    }
    
    # 获取用户输入的赛事标题
    title = input("请输入赛事标题: ")
    
    # 设置请求体（使用当前时间计算默认的开始和结束时间）
    current_time = int(time.time() * 1000)  # 当前时间（毫秒）
    start_time = current_time + 3600000  # 1小时后开始
    end_time = current_time + 10800000  # 3小时后结束
    
    payload = {
        "title": title,
        "start": start_time,
        "end": end_time
    }
    
    try:
        # 发送POST请求
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # 检查响应状态码
        if response.status_code == 200:
            return response.json()
        else:
            print(f"错误：请求返回状态码 {response.status_code}")
            print(f"响应内容：{response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"请求异常：{e}")
        return None


def delete_game():
    """
    删除赛事，运行时会提示用户输入赛事ID

    返回:
    bool: 删除成功返回True，失败返回False
    """
    # 获取用户输入的赛事ID
    game_id = input("请输入要删除的赛事ID: ")
    
    url = f"http://192.168.247.134/api/edit/games/{game_id}"
    
    # 设置请求头
    headers = {
        "Accept-Language": "zh-CN",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Origin": "http://192.168.247.134",
        "Referer": f"http://192.168.247.134/admin/games/{game_id}/info",
        "Cookie": "GZCTF_Token=CfDJ8Gu5Y0c4rA5FoOApV1A6BrQWCffHKUzFwvi837ikJuwqosAsVp2X6spqudA3GsQ7t7DbaQ4nQYpqisFEQBjycD8gvB87YrOebrV1vAtCQo9dmjEojHw3DYWLqdzLPVfmhY23xB9Xm2rya701cjfVtCUSn-5LD1OnRvmmD9jWht_eaFz8gJa2BootTbye64k-fN0HkUfB1y_3RL0tpZARay2ztOm5kqCsh8EVdzsrZrQUdhy_7xIzHOb6KGuFL6tCQ6qtyO5Ijn9nV_PZ6w_bo-9wNI2vzaQPFBNNP6QJsJflUjQAknSsTk33jdUcfeBS0BpcuNOzIewoupYauzAvPM9UCIxebqPVfaiPVdEkR-753p7xYCpaPTB_H0HaWdfVV_yTY0VBTpXUs5DZlQb90XKD7fh9h-FpqRfPLgsAhKFz-7UrvSuyD2msQ3rE6-EkFeMNFPym84haMpeifEThkJwvFa-LraUZ4M2QUjJdtUZEcN2dt70RECs17KB-rqKV6tuTwdg-5VsA-i8Hi53b0ZrFjKzdY89V4LxusXerEra0wGNUFEy5hjC8qBc8LjMF700kh_XnqKWJW-86k0wjrqB5Zb8eiupCugwrJoMyC6VebDruOoiyw-QaSB7p1T14pg3WdJ4y1ZA04M53mSVb-4HqxqqDc34uuiGpcLeXZ2x4Mzk6eq3CUbfcOaS65ZPxYRzffOJP9YCOo3PIdL4gU1M"
    }
    
    try:
        # 发送DELETE请求
        response = requests.delete(url, headers=headers)
        
        # 检查响应状态码
        if response.status_code == 200:
            print(f"成功删除赛事ID为 {game_id} 的赛事")
            return True
        else:
            print(f"错误：请求返回状态码 {response.status_code}")
            print(f"响应内容：{response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"请求异常：{e}")
        return False


def change_game():
    base_url = "http://192.168.247.134/api/edit/games"
    
    
    game_id = input("请输入要修改的赛事ID: ")
    new_title = input("请输入新的赛事标题: ")
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Accept-Language": "zh-CN",
        "Cookie": "GZCTF_Token=CfDJ8Gu5Y0c4rA5FoOApV1A6BrQWCffHKUzFwvi837ikJuwqosAsVp2X6spqudA3GsQ7t7DbaQ4nQYpqisFEQBjycD8gvB87YrOebrV1vAtCQo9dmjEojHw3DYWLqdzLPVfmhY23xB9Xm2rya701cjfVtCUSn-5LD1OnRvmmD9jWht_eaFz8gJa2BootTbye64k-fN0HkUfB1y_3RL0tpZARay2ztOm5kqCsh8EVdzsrZrQUdhy_7xIzHOb6KGuFL6tCQ6qtyO5Ijn9nV_PZ6w_bo-9wNI2vzaQPFBNNP6QJsJflUjQAknSsTk33jdUcfeBS0BpcuNOzIewoupYauzAvPM9UCIxebqPVfaiPVdEkR-753p7xYCpaPTB_H0HaWdfVV_yTY0VBTpXUs5DZlQb90XKD7fh9h-FpqRfPLgsAhKFz-7UrvSuyD2msQ3rE6-EkFeMNFPym84haMpeifEThkJwvFa-LraUZ4M2QUjJdtUZEcN2dt70RECs17KB-rqKV6tuTwdg-5VsA-i8Hi53b0ZrFjKzdY89V4LxusXerEra0wGNUFEy5hjC8qBc8LjMF700kh_XnqKWJW-86k0wjrqB5Zb8eiupCugwrJoMyC6VebDruOoiyw-QaSB7p1T14pg3WdJ4y1ZA04M53mSVb-4HqxqqDc34uuiGpcLeXZ2x4Mzk6eq3CUbfcOaS65ZPxYRzffOJP9YCOo3PIdL4gU1M"
    }
    
    # 先获取现有赛事数据
    get_url = f"{base_url}/{game_id}"
    try:
        response = requests.get(get_url, headers=headers)
        response.raise_for_status()
        game_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"获取赛事数据失败: {e}")
        return
    
    # 更新标题
    game_data["title"] = new_title
    
    # 发送更新请求
    put_url = f"{base_url}/{game_id}"
    try:
        response = requests.put(put_url, headers=headers, json=game_data)
        response.raise_for_status()
        print(f"赛事ID {game_id} 的标题已成功更新为: {new_title}")
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))
    except requests.exceptions.RequestException as e:
        print(f"更新赛事标题失败: {e}")
        if response.text:
            print("服务器返回内容:", response.text)

 
if __name__ == "__main__":
    print("开始尝试登录获取Cookie...\n")
    get_gzctf_token()

    games = get_games()
    for game in games:
        print(f"ID: {game['id']}, 标题: {game['title']}") 


    game_info = create_game()
    if game_info:
        print(f"成功创建赛事：{game_info['title']}")
        print(f"赛事ID：{game_info['id']}")
        print(f"开始时间：{game_info['start']}")
        print(f"结束时间：{game_info['end']}")

 
    if delete_game() :
        print("赛事删除操作已成功完成")
    else:
        print("赛事删除操作失败")
    
    change_game()   

    games = get_games()
    for game in games:
        print(f"ID: {game['id']}, 标题: {game['title']}") 