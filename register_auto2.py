import requests
import openpyxl
from pathlib import Path
import sys

def read_excel_data(file_path, column_mapping):
    """读取Excel中的注册信息"""
    if not Path(file_path).exists():
        print(f"❌ 错误：表格文件 '{file_path}' 不存在，请检查路径是否正确")
        return None
    
    try:
        # 加载Excel文件
        workbook = openpyxl.load_workbook(file_path, data_only=True)
        sheet = workbook.active  # 使用第一个工作表
        headers = [cell.value.strip() if cell.value else "" for cell in sheet[1]]  # 读取表头
        
        # 验证必要列是否存在
        required_cols = list(column_mapping.values())
        for col in required_cols:
            if col not in headers:
                print(f"❌ 错误：表格缺少必要列 '{col}'，请检查表头是否正确")
                workbook.close()
                return None
        
        # 提取数据
        data_list = []
        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            row_data = dict(zip(headers, row))
            # 构建注册信息（按接口字段映射）
            register_info = {
                "userName": row_data[column_mapping["userName"]],
                "password": row_data[column_mapping["password"]],
                "email": row_data[column_mapping["email"]]
            }
            
            # 检查数据完整性
            empty_fields = [k for k, v in register_info.items() if not v]
            if empty_fields:
                print(f"⚠️  警告：第 {row_num} 行缺少字段 {empty_fields}，已跳过")
                continue
            
            data_list.append(register_info)
        
        workbook.close()
        print(f"✅ 成功读取表格，共 {len(data_list)} 条有效注册信息")
        return data_list
    
    except Exception as e:
        print(f"❌ 读取表格失败：{str(e)}")
        return None

def get_request_headers(base_url):
    """生成请求头"""
    return {
        "Accept-Language": "zh-CN",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        "Origin": base_url,
        "Referer": f"{base_url}/account/register",
        "Connection": "keep-alive",
        "Accept-Encoding": "identity"
    }

def register_accounts(base_url, accounts_data):
    """批量注册账号"""
    register_url = f"{base_url}/api/account/register"
    headers = get_request_headers(base_url)
    
    print(f"\n开始向 {base_url} 批量注册账号...")
    success_count = 0
    
    for idx, account in enumerate(accounts_data, 1):
        print(f"\n===== 第 {idx} 个账号 =====")
        print(f"用户名: {account['userName']}")
        print(f"密码: {account['password']}")
        print(f"邮箱: {account['email']}")
        
        try:
            # 发送注册请求
            response = requests.post(
                url=register_url,
                json=account,
                headers=headers,
                timeout=15,
                verify=False  # 忽略SSL证书验证
            )
            
            # 输出响应信息
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text[:300]}")  # 显示前300字符
            
            # 验证注册结果
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get("status") == 200 and result.get("data") == "LoggedIn":
                        print("✅ 注册成功")
                        success_count += 1
                    else:
                        print(f"❌ 注册失败：{result.get('title', '未知错误')}")
                except:
                    print("❌ 注册失败：响应不是合法JSON格式")
            else:
                print(f"❌ 注册失败：状态码异常 ({response.status_code})")
        
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求出错：{str(e)}")
    
    print(f"\n===== 注册完成 =====")
    print(f"总数量: {len(accounts_data)}")
    print(f"成功数量: {success_count}")
    print(f"失败数量: {len(accounts_data) - success_count}")

def main():
    # 检查依赖
    try:
        import requests
        import openpyxl
    except ImportError as e:
        print(f"❌ 缺少必要依赖：{e.name}")
        print(f"请执行命令安装：pip install {e.name}")
        sys.exit(1)
    
    # 表格列名映射（可根据实际表格修改）
    column_mapping = {
        "userName": "userName",  # 表格中用户名的列名
        "password": "password",  # 表格中密码的列名
        "email": "email"         # 表格中邮箱的列名
    }
    
    # 交互式输入
    print("===== CTF批量注册工具 =====")
    base_url = input("\n请输入平台地址（例如 http://192.168.210.128）：").strip()
    if not base_url.startswith(("http://", "https://")):
        print("❌ 错误：地址必须以 http:// 或 https:// 开头")
        sys.exit(1)
    
    excel_path = input("请输入Excel表格路径（例如 C:/ctf_accounts.xlsx）：").strip()
    accounts_data = read_excel_data(excel_path, column_mapping)
    if not accounts_data:
        sys.exit(1)
    
    # 开始注册
    requests.packages.urllib3.disable_warnings()  # 禁用SSL警告
    register_accounts(base_url, accounts_data)

if __name__ == "__main__":
    main()