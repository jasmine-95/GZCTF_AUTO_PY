import requests
import json
import time
from typing import Optional,List,Dict

class GZCTFClient:
    """GZCTF平台API客户端"""
    
    def __init__(self, base_url="http://10.52.84.140:8000"):
        """初始化客户端
        
        Args:
            base_url: API基础URL
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        
    def login(self, username="Admin", password="1=uW_-lJ7_c7wi6q"):
        """登录系统获取GZCTF_Token Cookie
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            bool: 登录成功返回True，失败返回False
        """
        # 登录API端点
        url = f"{self.base_url}/api/account/login"
        
        # 请求头信息
        headers = {
            "Host": self.base_url.split("//")[1],
            "Content-Length": "47",
            "Accept-Language": "zh-CN",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/account/login?from=/",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        
        # 登录数据
        payload = {
            "userName": username,
            "password": password
        }
        
        try:
            # 发送POST请求
            response = self.session.post(url, headers=headers, data=json.dumps(payload), timeout=10)
            
            # 检查响应状态
            if response.status_code == 200:
                # 从响应头中获取Cookie
                cookies = response.cookies
                
                # 查找GZCTF_Token
                for cookie in cookies:
                    if cookie.name == "GZCTF_Token":
                        self.token = cookie.value
                        # 保存到文件
                        with open("cookie.txt", "w") as f:
                            f.write(f"GZCTF_Token={self.token}\n")
                        print(f"成功获取GZCTF_Token，已保存到cookie.txt")
                        
                        # 在终端显示
                        print("\n===== GZCTF_Token 信息 =====")
                        print(f"名称: GZCTF_Token")
                        print(f"值: {self.token}")
                        print(f"保存时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                        print("==========================\n")
                        return True
                
                print("未找到GZCTF_Token Cookie")
                return False
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {e}")
            return False
        except Exception as e:
            print(f"发生错误: {e}")
            return False
    
    def get_games(self, count=30, skip=0):
        """获取竞赛列表，返回id和title信息
        
        Args:
            count: 获取数量
            skip: 跳过数量
            
        Returns:
            list: 竞赛列表，每个元素包含id和title
        """
        if not self.token:
            print("请先登录获取Token")
            return []
            
        url = f"{self.base_url}/api/edit/games?count={count}&skip={skip}"
        headers = {
            "Accept-Language": "zh-CN",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "Referer": f"{self.base_url}/admin/games",
            "Cookie": f"GZCTF_Token={self.token}"
        }

        try:
            response = self.session.get(url, headers=headers)
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
    
    def create_game(self, title=None):
        """
        创建新赛事
        
        Args:
            title: 赛事标题，如果为None则提示用户输入
            
        Returns:
            dict: 包含赛事信息的字典，如果出错则返回None
        """
        if not self.token:
            print("请先登录获取Token")
            return None
            
        url = f"{self.base_url}/api/edit/games"
        
        # 设置请求头
        headers = {
            "Accept-Language": "zh-CN",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/admin/games",
            "Cookie": f"GZCTF_Token={self.token}"
        }
        
        # 获取赛事标题
        if title is None:
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
            response = self.session.post(url, headers=headers, data=json.dumps(payload))
            
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
    
    def delete_game(self, game_id=None):
        """
        删除赛事
        
        Args:
            game_id: 赛事ID，如果为None则提示用户输入
            
        Returns:
            bool: 删除成功返回True，失败返回False
        """
        if not self.token:
            print("请先登录获取Token")
            return False
            
        # 获取赛事ID
        if game_id is None:
            game_id = input("请输入要删除的赛事ID: ")
        
        url = f"{self.base_url}/api/edit/games/{game_id}"
        
        # 设置请求头
        headers = {
            "Accept-Language": "zh-CN",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/admin/games/{game_id}/info",
            "Cookie": f"GZCTF_Token={self.token}"
        }
        
        try:
            # 发送DELETE请求
            response = self.session.delete(url, headers=headers)
            
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
    
    def change_game(self, game_id=None, new_title=None):
        """
        修改赛事标题
        
        Args:
            game_id: 赛事ID，如果为None则提示用户输入
            new_title: 新标题，如果为None则提示用户输入
            
        Returns:
            bool: 修改成功返回True，失败返回False
        """
        if not self.token:
            print("请先登录获取Token")
            return False
            
        # 获取赛事ID和新标题
        if game_id is None:
            game_id = input("请输入要修改的赛事ID: ")
        if new_title is None:
            new_title = input("请输入新的赛事标题: ")
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Language": "zh-CN",
            "Cookie": f"GZCTF_Token={self.token}"
        }
        
        # 先获取现有赛事数据
        get_url = f"{self.base_url}/api/edit/games/{game_id}"
        try:
            response = self.session.get(get_url, headers=headers)
            response.raise_for_status()
            game_data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"获取赛事数据失败: {e}")
            return False
        
        # 更新标题
        game_data["title"] = new_title
        
        # 发送更新请求
        put_url = f"{self.base_url}/api/edit/games/{game_id}"
        try:
            response = self.session.put(put_url, headers=headers, json=game_data)
            response.raise_for_status()
            print(f"赛事ID {game_id} 的标题已成功更新为: {new_title}")
            print(json.dumps(response.json(), ensure_ascii=False, indent=2))
            return True
        except requests.exceptions.RequestException as e:
            print(f"更新赛事标题失败: {e}")
            if response.text:
                print("服务器返回内容:", response.text)
            return False


if __name__ == "__main__":
    # 创建客户端实例
    client = GZCTFClient()
    
    # 登录
    print("开始尝试登录获取Cookie...\n")
    if client.login():
        # 获取赛事列表
        games = client.get_games()
        for game in games:
            print(f"ID: {game['id']}, 标题: {game['title']}") 
        
        # 创建赛事
        game_info = client.create_game()
        if game_info:
            print(f"成功创建赛事：{game_info['title']}")
            print(f"赛事ID：{game_info['id']}")
            print(f"开始时间：{game_info['start']}")
            print(f"结束时间：{game_info['end']}")
        
        # 删除赛事
        if client.delete_game():
            print("赛事删除操作已成功完成")
        else:
            print("赛事删除操作失败")
        
        # 修改赛事
        client.change_game()
        
        # 再次获取赛事列表
        games = client.get_games()
        for game in games:
            print(f"ID: {game['id']}, 标题: {game['title']}")