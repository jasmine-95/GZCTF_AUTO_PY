import requests
import json
import time
from typing import Optional, List, Dict

class GZCTFClient:
    """GZCTF平台API客户端（完整实现所有必要方法，包含create_game）"""
    
    def __init__(self, base_url: str, cookie_file: str = "cookie.txt"):
        self.base_url = base_url.rstrip('/')
        self.cookie_file = cookie_file
        self.session = requests.Session()
        self.token = None
        
        # 容器配置核心字段
        self.CONTAINER_FIELDS = [
            "containerImage", "memoryLimit", "cpuCount", 
            "storageLimit", "containerExposePort", "enableTrafficCapture"
        ]
        self.DEFAULT_CONTAINER = {
            "containerImage": "ctftraining/ciscn_2019_southeastern_china_web4:latest",
            "memoryLimit": 64,
            "cpuCount": 1,
            "storageLimit": 256,
            "containerExposePort": 80,
            "enableTrafficCapture": False
        }
        self.CATEGORIES = ["Misc", "Crypto", "Pwn", "Web", "Reverse", "Blockchain", 
                         "Forensics", "Hardware", "Mobile", "PPC", "AI", "Pentest", "OSINT"]
        self.TYPES = ["StaticAttachment", "StaticContainer", "DynamicAttachment", "DynamicContainer"]
        
        self._load_token_from_file()
    
    def _load_token_from_file(self):
        try:
            with open(self.cookie_file, "r") as f:
                for line in f:
                    if line.startswith("GZCTF_Token="):
                        self.token = line.strip().split("=", 1)[1]
                        print(f"已从{self.cookie_file}加载{self.base_url}的Token")
                        return
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"加载{self.base_url}的Token失败: {e}")
      
    def _save_token_to_file(self):
        if self.token:
            try:
                with open(self.cookie_file, "w") as f:
                    f.write(f"GZCTF_Token={self.token}\n")
                print(f"已保存{self.base_url}的Token到{self.cookie_file}")
            except Exception as e:
                print(f"保存{self.base_url}的Token失败: {e}")
    
    def _handle_url_error(self, e: requests.exceptions.RequestException) -> bool:
        if isinstance(e, (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL)):
            print(f"访问{self.base_url}失败: {e}")
            print("建议检查:")
            print(f"- 平台URL是否正确: {self.base_url}")
            print("- 网络连接或服务器状态")
            return True
        return False
    
    def login(self, username: str = "Admin", password: str = "Admin_123_nya") -> bool:
        url = f"{self.base_url}/api/account/login"
        headers = {
            "Host": self.base_url.split("//")[1],
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/account/login?from=/",
        }
        payload = {"userName": username, "password": password}
        
        try:
            response = self.session.post(url, headers=headers, data=json.dumps(payload), timeout=10)
            if response.status_code == 200:
                for cookie in response.cookies:
                    if cookie.name == "GZCTF_Token":
                        self.token = cookie.value
                        self._save_token_to_file()
                        print(f"{self.base_url}登录成功")
                        return True
                print(f"{self.base_url}登录失败：未获取到Token")
                return False
            else:
                print(f"{self.base_url}登录失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text[:100]}...")
                return False
        except requests.exceptions.RequestException as e:
            if self._handle_url_error(e):
                return False
            print(f"{self.base_url}登录请求异常: {e}")
            return False
    
    def get_games(self, count: int = 30, skip: int = 0) -> List[Dict]:
        if not self.token:
            print(f"{self.base_url}未登录，请先登录")
            return []
            
        url = f"{self.base_url}/api/edit/games?count={count}&skip={skip}"
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Referer": f"{self.base_url}/admin/games",
            "Cookie": f"GZCTF_Token={self.token}"
        }

        try:
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            games = data.get("data", []) if isinstance(data, dict) else data
            return [{"id": game.get("id"), "title": game.get("title")} for game in games]
        except requests.exceptions.RequestException as e:
            if self._handle_url_error(e):
                return []
            print(f"{self.base_url}获取赛事列表失败: {e}")
            return []
    
    def get_game_details(self, game_id: int) -> Optional[Dict]:
        if not self.token:
            print(f"{self.base_url}未登录，请先登录")
            return None
            
        url = f"{self.base_url}/api/edit/games/{game_id}"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Referer": f"{self.base_url}/admin/games/{game_id}/info",
            "Cookie": f"GZCTF_Token={self.token}"
        }

        try:
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if self._handle_url_error(e):
                return None
            print(f"{self.base_url}获取赛事{game_id}详情失败: {e}")
            return None
    
    def get_challenges(self, game_id: int) -> List[Dict]:
        if not self.token:
            print(f"{self.base_url}未登录，请先登录")
            return []
            
        url = f"{self.base_url}/api/edit/games/{game_id}/challenges"
        headers = {
            "Accept-Language": "zh-CN",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Referer": f"{self.base_url}/admin/games/{game_id}/challenges",
            "Cookie": f"GZCTF_Token={self.token}"
        }

        try:
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            challenges = data.get("data", []) if isinstance(data, dict) else data
            if not isinstance(challenges, list):
                challenges = []
            
            return [
                {
                    "id": c.get("id"),
                    "title": c.get("title"),
                    "category": c.get("category"),
                    "type": c.get("type")
                }
                for c in challenges
            ]
        except requests.exceptions.RequestException as e:
            if self._handle_url_error(e):
                return []
            print(f"{self.base_url}获取赛事{game_id}的题目失败: {e}")
            return []
    
    def get_challenge_details(self, game_id: int, challenge_id: int) -> Optional[Dict]:
        if not self.token:
            print(f"{self.base_url}未登录，请先登录")
            return None
            
        url = f"{self.base_url}/api/edit/games/{game_id}/challenges/{challenge_id}"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Referer": f"{self.base_url}/admin/games/{game_id}/challenges/{challenge_id}",
            "Cookie": f"GZCTF_Token={self.token}"
        }
        
        try:
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            challenge_data = response.json()
            # 验证是否获取到关键字段
            required_fields = ["content", "hints", "title", "category"]
            missing_fields = [f for f in required_fields if f not in challenge_data]
            if missing_fields:
                print(f"警告：题目{challenge_id}缺失字段: {missing_fields}")
            else:
                print(f"✅ 题目{challenge_id}获取成功：content={challenge_data['content']}, hints={challenge_data['hints']}")
            return challenge_data
        except requests.exceptions.RequestException as e:
            if self._handle_url_error(e):
                return None
            print(f"{self.base_url}获取题目{challenge_id}详情失败: {e}")
            return None
    
    # 修复：完整实现create_game方法
    def create_game(self, game_data: Dict) -> Optional[Dict]:
        if not self.token:
            print(f"{self.base_url}未登录，请先登录")
            return None
            
        url = f"{self.base_url}/api/edit/games"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/admin/games",
            "Cookie": f"GZCTF_Token={self.token}"
        }
        
        try:
            response = self.session.post(url, headers=headers, data=json.dumps(game_data))
            if response.status_code == 200:
                result = response.json()
                print(f"{self.base_url}创建赛事成功，新ID: {result.get('id')}")
                return result
            else:
                print(f"{self.base_url}创建赛事失败，状态码: {response.status_code}")
                print(f"响应: {response.text[:200]}...")
                return None
        except requests.exceptions.RequestException as e:
            if self._handle_url_error(e):
                return None
            print(f"{self.base_url}创建赛事请求异常: {e}")
            return None
    
    def create_challenge(self, game_id: int, challenge_data: Dict) -> Optional[Dict]:
        if not self.token:
            print(f"{self.base_url}未登录，请先登录")
            return None
            
        url = f"{self.base_url}/api/edit/games/{game_id}/challenges"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/admin/games/{game_id}/challenges",
            "Cookie": f"GZCTF_Token={self.token}"
        }
        
        try:
            # 仅提交创建题目必需的基础字段
            basic_required = ["title", "category", "type", "score"]
            create_payload = {k: v for k, v in challenge_data.items() if k in basic_required}
            # 补充默认值
            create_payload.setdefault("score", 100)
            create_payload.setdefault("flag", f"flag{{{create_payload['title']}_temp}}")
            
            response = self.session.post(url, headers=headers, data=json.dumps(create_payload))
            if response.status_code == 200:
                result = response.json()
                print(f"{self.base_url}创建题目基础结构成功，新ID: {result.get('id')}")
                return result
            else:
                print(f"{self.base_url}创建题目失败，状态码: {response.status_code}")
                print(f"响应: {response.text[:200]}...")
                return None
        except requests.exceptions.RequestException as e:
            if self._handle_url_error(e):
                return None
            print(f"{self.base_url}创建题目请求异常: {e}")
            return None
    
    def update_challenge_full(self, game_id: int, challenge_id: int, full_data: Dict) -> bool:
        """全量更新题目所有字段（对应PUT请求）"""
        if not self.token:
            print(f"{self.base_url}未登录，无法全量更新题目")
            return False
            
        url = f"{self.base_url}/api/edit/games/{game_id}/challenges/{challenge_id}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/admin/games/{game_id}/challenges/{challenge_id}",
            "Cookie": f"GZCTF_Token={self.token}"
        }
        
        try:
            # 获取目标平台当前题目信息
            target_current = self.get_challenge_details(game_id, challenge_id)
            if not target_current:
                print(f"无法获取目标题目{challenge_id}当前信息，更新失败")
                return False
            
            # 合并全量数据
            merged_data = target_current.copy()
            for key, value in full_data.items():
                if key != "id":  # 排除ID
                    merged_data[key] = value
            
            # 强制设置兼容字段
            merged_data["category"] = merged_data["category"] if merged_data["category"] in self.CATEGORIES else "Misc"
            merged_data["type"] = merged_data["type"] if merged_data["type"] in self.TYPES else "StaticAttachment"
            
            # 发送PUT请求全量更新
            print(f"📤 全量更新题目{challenge_id}：content={merged_data['content']}, hints={merged_data['hints']}")
            response = self.session.put(url, headers=headers, data=json.dumps(merged_data))
            
            if response.status_code == 200:
                # 验证更新结果
                updated = response.json()
                if updated.get("content") == full_data.get("content") and updated.get("hints") == full_data.get("hints"):
                    print(f"✅ 题目{challenge_id}全量信息更新成功")
                    return True
                else:
                    print(f"⚠️ 题目{challenge_id}更新后字段不匹配：")
                    print(f"  期望content: {full_data.get('content')}，实际: {updated.get('content')}")
                    print(f"  期望hints: {full_data.get('hints')}，实际: {updated.get('hints')}")
                    return False
            else:
                print(f"更新题目失败，状态码: {response.status_code}")
                print(f"响应: {response.text[:200]}...")
                return False
                
        except requests.exceptions.RequestException as e:
            if self._handle_url_error(e):
                return False
            print(f"全量更新题目请求异常: {e}")
            return False
    
    def update_challenge_container(self, game_id: int, challenge_id: int, container_data: Dict) -> bool:
        """更新题目容器配置"""
        if not self.token:
            print(f"{self.base_url}未登录，无法更新容器配置")
            return False
            
        url = f"{self.base_url}/api/edit/games/{game_id}/challenges/{challenge_id}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/admin/games/{game_id}/challenges/{challenge_id}",
            "Cookie": f"GZCTF_Token={self.token}"
        }
        
        try:
            current = self.get_challenge_details(game_id, challenge_id)
            if not current:
                print(f"无法获取题目{challenge_id}当前信息，更新容器配置失败")
                return False
                
            # 合并容器配置
            for field in self.CONTAINER_FIELDS:
                if field in container_data:
                    current[field] = container_data[field]
            
            response = self.session.put(url, headers=headers, data=json.dumps(current))
            if response.status_code == 200:
                print(f"{self.base_url}题目{challenge_id}容器配置更新成功")
                return True
            else:
                print(f"更新容器配置失败，状态码: {response.status_code}")
                print(f"响应: {response.text[:100]}...")
                return False
                
        except requests.exceptions.RequestException as e:
            if self._handle_url_error(e):
                return False
            print(f"更新容器配置请求异常: {e}")
            return False


class CrossPlatformCopier:
    """跨平台赛事复制工具"""
    
    def __init__(self, source_client: GZCTFClient, target_client: GZCTFClient):
        self.source = source_client
        self.target = target_client
    
    def _transform_game_data(self, source_data: Dict) -> Dict:
        """转换赛事数据"""
        current_ts = int(time.time() * 1000)
        if 'start' not in source_data:
            source_data['start'] = current_ts + 3600000  # 1小时后开始
        if 'end' not in source_data:
            source_data['end'] = current_ts + 10800000    # 3小时后结束
    
        if 'id' in source_data:
           del source_data['id']

        return source_data
    
    def _extract_container_data(self, challenge_details: Dict) -> Dict:
        """提取容器配置"""
        container_data = {}
        for field in self.target.CONTAINER_FIELDS:
            container_data[field] = challenge_details.get(field) or self.target.DEFAULT_CONTAINER[field]
        
        if "port" in challenge_details and "containerExposePort" not in container_data:
            container_data["containerExposePort"] = challenge_details["port"]
            
        return container_data
    
    def copy_game(self):
        """完整复制赛事（包含所有题目及字段信息）"""
        if not self.source.token or not self.target.token:
            print("源平台或目标平台未登录，请先完成登录")
            return False
        
        # 获取源平台赛事列表
        print(f"\n===== 加载{self.source.base_url}的赛事列表 =====")
        source_games = self.source.get_games()
        if not source_games:
            print("源平台没有可用赛事")
            return False
        
        # 显示并选择源赛事
        print("\n源平台可用赛事:")
        for i, game in enumerate(source_games, 1):
            print(f"{i}. {game['title']} (ID: {game['id']})")
        
        while True:
            try:
                choice = input("\n请选择要复制的赛事编号 (0返回): ")
                if choice == "0":
                    return False
                idx = int(choice) - 1
                if 0 <= idx < len(source_games):
                    source_game = source_games[idx]
                    source_game_id = source_game["id"]
                    source_game_title = source_game["title"]
                    print(f"已选择源赛事: 《{source_game_title}》(ID: {source_game_id})")
                    break
                else:
                    print(f"请输入1-{len(source_games)}之间的编号")
            except ValueError:
                print("请输入有效的数字")
        
        # 获取源赛事详情
        print("\n获取源赛事详情...")
        source_game_details = self.source.get_game_details(source_game_id)
        if not source_game_details:
            print("获取源赛事详情失败，无法继续")
            return False
        
        # 创建目标赛事
        target_title = input(f"\n请输入目标赛事名称 (默认: 复制_{source_game_title}): ") or f"复制_{source_game_title}"
        print("\n在目标平台创建赛事...")
        target_game_data = self._transform_game_data(source_game_details)
        target_game_data["title"] = target_title
        target_game = self.target.create_game(target_game_data)
        if not target_game or not target_game.get("id"):
            print("创建目标赛事失败")
            return False
        target_game_id = target_game["id"]
        
        # 获取源赛事题目列表
        print(f"\n获取源赛事《{source_game_title}》的题目列表...")
        source_challenges = self.source.get_challenges(source_game_id)
        if not source_challenges:
            print("源赛事没有题目，复制完成")
            return True
        
        # 复制所有题目
        print(f"\n开始复制{len(source_challenges)}个题目...")
        success_count = 0
        
        for i, challenge in enumerate(source_challenges, 1):
            print(f"\n处理题目 {i}/{len(source_challenges)}: {challenge['title']}")
            
            # 获取完整题目详情
            full_challenge = self.source.get_challenge_details(source_game_id, challenge["id"])
            if not full_challenge:
                print(f"⚠️ 跳过：无法获取题目{challenge['id']}的详情")
                continue
            
            # 1. 创建题目基础结构
            basic_data = {
                "title": full_challenge["title"],
                "category": full_challenge["category"],
                "type": full_challenge["type"],
                "score": full_challenge.get("originalScore", 100)
            }
            target_challenge = self.target.create_challenge(target_game_id, basic_data)
            if not target_challenge or not target_challenge.get("id"):
                print(f"⚠️ 题目{challenge['title']}创建失败，继续下一题")
                continue
            target_challenge_id = target_challenge["id"]
            
            # 2. 全量更新所有字段
            update_success = self.target.update_challenge_full(
                target_game_id, 
                target_challenge_id, 
                full_challenge
            )
            if not update_success:
                print(f"⚠️ 题目{challenge['title']}全量信息更新失败")
                continue
            
            # 3. 处理容器配置
            if full_challenge["type"] in ["StaticContainer", "DynamicContainer"]:
                container_data = self._extract_container_data(full_challenge)
                print(f"准备复制容器配置: {container_data}")
                self.target.update_challenge_container(
                    target_game_id, 
                    target_challenge_id, 
                    container_data
                )
            
            success_count += 1
        
        # 输出结果
        print(f"\n===== 复制完成 =====")
        print(f"源赛事: {self.source.base_url} 《{source_game_title}》(ID: {source_game_id})")
        print(f"目标赛事: {self.target.base_url} 《{target_title}》(ID: {target_game_id})")
        print(f"题目复制结果: {success_count}/{len(source_challenges)} 成功")
        return True


# 主程序
if __name__ == "__main__":
    print("===== GZCTF跨平台赛事复制工具 =====")
    
    # 配置源平台
    print("\n===== 配置源平台 =====")
    source_url = input("请输入源平台URL (默认: http://192.168.1.168): ") or "http://192.168.1.168"
    source_client = GZCTFClient(source_url, cookie_file="source_cookie.txt")
    
    # 配置目标平台
    print("\n===== 配置目标平台 =====")
    target_url = input("请输入目标平台URL (默认: http://192.168.1.17): ") or "http://192.168.1.17"
    target_client = GZCTFClient(target_url, cookie_file="target_cookie.txt")
    
    # 登录流程
    if not source_client.token:
        print(f"\n登录源平台 {source_url}...")
        source_user = input("用户名 (默认Admin): ") or "Admin"
        source_pwd = input("密码 (默认Admin_123_nya): ") or "Admin_123_nya"
        if not source_client.login(source_user, source_pwd):
            print("源平台登录失败，程序退出")
            exit(1)
    
    if not target_client.token:
        print(f"\n登录目标平台 {target_url}...")
        target_user = input("用户名 (默认Admin): ") or "Admin"
        target_pwd = input("密码 (默认Admin_123_nya): ") or "Admin_123_nya"
        if not target_client.login(target_user, target_pwd):
            print("目标平台登录失败，程序退出")
            exit(1)
    
    # 创建跨平台复制器
    copier = CrossPlatformCopier(source_client, target_client)
    
    # 主菜单
    while True:
        print("\n===== 主菜单 =====")
        print("1. 跨平台复制赛事（含所有题目信息）")
        print("2. 查看源平台赛事列表")
        print("3. 查看目标平台赛事列表")
        print("4. 退出")
        
        choice = input("请选择操作 (1-4): ")
        if choice == "1":
            copier.copy_game()
        elif choice == "2":
            games = source_client.get_games()
            print(f"\n{source_client.base_url}的赛事列表:")
            for i, g in enumerate(games, 1):
                print(f"{i}. {g['title']} (ID: {g['id']})")
        elif choice == "3":
            games = target_client.get_games()
            print(f"\n{target_client.base_url}的赛事列表:")
            for i, g in enumerate(games, 1):
                print(f"{i}. {g['title']} (ID: {g['id']})")
        elif choice == "4":
            print("程序已退出")
            break
        else:
            print("无效选择，请输入1-4")
    