import requests
import json
import time

# 基础配置
BASE_URL = "http://localhost:5000"
CLASSIFY_URL = f"{BASE_URL}/classify/"
TRIAGE_URL = f"{BASE_URL}/triage/"
HEADERS = {"Content-Type": "application/json; charset=utf-8"}

def test_full_workflow():
    """测试完整的分类→缓存→分诊流程"""
    print("="*50)
    print("开始测试完整流程")
    print("="*50)
    
    # 第一步：症状分类
    print("\n>>> 步骤1: 调用症状分类接口")
    symptoms = ["眼痛", "头痛", "视力模糊"]
    classify_response = requests.post(
        CLASSIFY_URL,
        headers=HEADERS,
        json={"symptoms": symptoms}
    )
    
    # 检查分类响应
    if classify_response.status_code != 200:
        print(f"分类接口失败: {classify_response.status_code}")
        print(classify_response.text)
        return
    
    classify_data = classify_response.json()
    print("分类接口响应:")
    print(json.dumps(classify_data, ensure_ascii=False, indent=2))
    
    # 提取关键信息
    result_id = classify_data["result_id"]
    disease_name = classify_data["classification"]["disease"]
    
    # 第二步：获取缓存结果
    print("\n>>> 步骤2: 调用缓存获取接口")
    cache_url = f"{BASE_URL}/classify/result/{result_id}"
    cache_response = requests.get(cache_url, headers=HEADERS)
    
    # 检查缓存响应
    if cache_response.status_code != 200:
        print(f"缓存接口失败: {cache_response.status_code}")
        print(cache_response.text)
        return
    
    cache_data = cache_response.json()
    print("缓存接口响应:")
    print(json.dumps(cache_data, ensure_ascii=False, indent=2))
    
    # 第三步：急诊分诊（新版接口）
    print("\n>>> 步骤3: 调用新版急诊分诊接口")
    
    # 根据疾病类型构造分诊数据
    if "青光眼" in disease_name:
        triage_data = {
            "session_id": result_id,
            "pain_level": "剧痛",
            "vision_changes": ["视力急剧下降", "虹视现象"],
            "duration_hours": 6,
            "associated_symptoms": ["恶心呕吐", "剧烈头痛"],
            "trauma_history": False,
            "chemical_exposure": False
        }
    elif "视网膜" in disease_name:
        triage_data = {
            "session_id": result_id,
            "pain_level": "中度疼痛",
            "vision_changes": ["视力突然完全丧失", "眼前有黑影"],
            "duration_hours": 12,
            "associated_symptoms": [],
            "trauma_history": False,
            "chemical_exposure": False
        }
    else:  # 其他疾病（如结膜炎）
        triage_data = {
            "session_id": result_id,
            "pain_level": "轻微不适",
            "vision_changes": ["看东西模糊"],
            "duration_hours": 48,
            "associated_symptoms": ["眼红", "分泌物多"],
            "trauma_history": False,
            "chemical_exposure": False
        }
    
    print("构造的分诊请求数据:")
    print(json.dumps(triage_data, ensure_ascii=False, indent=2))
    
    try:
        triage_response = requests.post(
            TRIAGE_URL,
            headers=HEADERS,
            json=triage_data,
            timeout=10
        )
    except Exception as e:
        print(f"分诊接口请求失败: {str(e)}")
        return
    
    # 检查分诊响应
    if triage_response.status_code != 200:
        print(f"分诊接口失败: {triage_response.status_code}")
        print(f"错误响应: {triage_response.text}")
        return
    
    triage_result = triage_response.json()
    print("分诊接口响应:")
    print(json.dumps(triage_result, ensure_ascii=False, indent=2))
    
    # 第四步：调试接口（可选）
    print("\n>>> 步骤4: 调用调试接口（可选）")
    debug_url = f"{BASE_URL}/classify/session/{result_id}"
    debug_response = requests.get(debug_url, headers=HEADERS, timeout=10)
    
    if debug_response.status_code == 200:
        debug_data = debug_response.json()
        print("调试接口响应:")
        print(json.dumps(debug_data, ensure_ascii=False, indent=2))
    else:
        print(f"调试接口不可用: {debug_response.status_code}")
    
    print("\n" + "="*50)
    print("测试完成!")
    print("="*50)

def test_level1_emergency():
    """测试1级急症（需要立即就诊的情况）"""
    print("\n" + "="*50)
    print("测试1级急症（需要立即就诊）")
    print("="*50)
    
    # 先获取分类结果
    print("\n>>> 创建分类结果")
    symptoms = ["眼痛", "视力模糊"]
    classify_response = requests.post(
        CLASSIFY_URL,
        headers=HEADERS,
        json={"symptoms": symptoms}
    )
    
    if classify_response.status_code != 200:
        print(f"分类接口失败: {classify_response.status_code}")
        return
    
    classify_data = classify_response.json()
    result_id = classify_data["result_id"]
    disease_name = classify_data["classification"]["disease"]
    
    # 构造1级急症的分诊数据
    print("\n>>> 构造1级急症分诊数据")
    triage_data = {
        "session_id": result_id,
        "pain_level": "剧痛",
        "vision_changes": ["视力突然完全丧失"],
        "duration_hours": 2,
        "associated_symptoms": ["化学物质进入眼睛"],
        "trauma_history": True,
        "chemical_exposure": True
    }
    
    print("分诊请求数据:")
    print(json.dumps(triage_data, ensure_ascii=False, indent=2))
    
    # 调用分诊接口
    triage_response = requests.post(
        TRIAGE_URL,
        headers=HEADERS,
        json=triage_data
    )
    
    if triage_response.status_code != 200:
        print(f"分诊接口失败: {triage_response.status_code}")
        print(triage_response.text)
        return
    
    triage_result = triage_response.json()
    print("分诊结果:")
    print(json.dumps(triage_result, ensure_ascii=False, indent=2))
    
    # 验证是否为1级
    if triage_result['triage_result']['level'] == 1:
        print("✅ 测试通过：正确识别为1级急症")
    else:
        print("❌ 测试失败：未正确识别为1级急症")
    
    print("\n" + "="*50)
    print("1级急症测试完成!")
    print("="*50)

def test_level2_emergency():
    """测试2级急症（需要当天就诊的情况）"""
    print("\n" + "="*50)
    print("测试2级急症（需要当天就诊）")
    print("="*50)
    
    # 先获取分类结果
    print("\n>>> 创建分类结果")
    symptoms = ["眼痛", "视力急剧下降"]
    classify_response = requests.post(
        CLASSIFY_URL,
        headers=HEADERS,
        json={"symptoms": symptoms}
    )
    
    if classify_response.status_code != 200:
        print(f"分类接口失败: {classify_response.status_code}")
        return
    
    classify_data = classify_response.json()
    result_id = classify_data["result_id"]
    
    # 构造2级急症的分诊数据
    print("\n>>> 构造2级急症分诊数据")
    triage_data = {
        "session_id": result_id,
        "pain_level": "剧痛",
        "vision_changes": ["视力急剧下降", "眼前有黑影"],
        "duration_hours": 6,
        "associated_symptoms": [],
        "trauma_history": False,
        "chemical_exposure": False
    }
    
    print("分诊请求数据:")
    print(json.dumps(triage_data, ensure_ascii=False, indent=2))
    
    # 调用分诊接口
    triage_response = requests.post(
        TRIAGE_URL,
        headers=HEADERS,
        json=triage_data
    )
    
    if triage_response.status_code != 200:
        print(f"分诊接口失败: {triage_response.status_code}")
        print(triage_response.text)
        return
    
    triage_result = triage_response.json()
    print("分诊结果:")
    print(json.dumps(triage_result, ensure_ascii=False, indent=2))
    
    # 验证是否为2级
    if triage_result['triage_result']['level'] == 2:
        print("✅ 测试通过：正确识别为2级急症")
    else:
        print("❌ 测试失败：未正确识别为2级急症")
    
    print("\n" + "="*50)
    print("2级急症测试完成!")
    print("="*50)

def test_level4_routine():
    """测试4级常规问题（48小时内就诊）"""
    print("\n" + "="*50)
    print("测试4级常规问题")
    print("="*50)
    
    # 先获取分类结果
    print("\n>>> 创建分类结果")
    symptoms = ["眼红", "异物感"]
    classify_response = requests.post(
        CLASSIFY_URL,
        headers=HEADERS,
        json={"symptoms": symptoms}
    )
    
    if classify_response.status_code != 200:
        print(f"分类接口失败: {classify_response.status_code}")
        return
    
    classify_data = classify_response.json()
    result_id = classify_data["result_id"]
    
    # 构造常规问题的分诊数据
    print("\n>>> 构造常规问题分诊数据")
    triage_data = {
        "session_id": result_id,
        "pain_level": "轻微不适",
        "vision_changes": ["看东西模糊"],
        "duration_hours": 72,
        "associated_symptoms": ["眼红", "分泌物多"],
        "trauma_history": False,
        "chemical_exposure": False
    }
    
    print("分诊请求数据:")
    print(json.dumps(triage_data, ensure_ascii=False, indent=2))
    
    # 调用分诊接口
    triage_response = requests.post(
        TRIAGE_URL,
        headers=HEADERS,
        json=triage_data
    )
    
    if triage_response.status_code != 200:
        print(f"分诊接口失败: {triage_response.status_code}")
        print(triage_response.text)
        return
    
    triage_result = triage_response.json()
    print("分诊结果:")
    print(json.dumps(triage_result, ensure_ascii=False, indent=2))
    
    # 验证是否为4级
    if triage_result['triage_result']['level'] == 4:
        print("✅ 测试通过：正确识别为4级常规问题")
    else:
        print("❌ 测试失败：未正确识别为4级常规问题")
    
    print("\n" + "="*50)
    print("常规问题测试完成!")
    print("="*50)

def test_error_cases():
    """测试各种错误情况"""
    print("\n" + "="*50)
    print("开始测试错误情况")
    print("="*50)
    
    # 情况1: 无效的症状输入
    print("\n>>> 情况1: 空症状列表")
    response = requests.post(
        CLASSIFY_URL,
        headers=HEADERS,
        json={"symptoms": []}
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
    
    # 情况2: 无效的缓存ID
    print("\n>>> 情况2: 无效的缓存ID")
    response = requests.get(
        f"{BASE_URL}/classify/result/invalid_id",
        headers=HEADERS
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
    
    # 情况3: 过期的session_id
    print("\n>>> 情况3: 过期的session_id")
    # 创建一个结果并等待过期
    response = requests.post(
        CLASSIFY_URL,
        headers=HEADERS,
        json={"symptoms": ["眼红", "异物感"]}
    )
    if response.status_code == 200:
        result_id = response.json()["result_id"]
        print(f"创建结果 {result_id}, 等待过期...")
        time.sleep(65)  # 等待超过10分钟（根据clean_expired_cache设置）
        
        # 尝试获取过期结果
        response = requests.get(
            f"{BASE_URL}/classify/result/{result_id}",
            headers=HEADERS
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    
    # 情况4: 分诊接口缺少必要参数
    print("\n>>> 情况4: 分诊接口缺少必要参数")
    response = requests.post(
        TRIAGE_URL,
        headers=HEADERS,
        json={"session_id": "invalid_id"}  # 缺少其他参数
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
    
    print("\n" + "="*50)
    print("错误测试完成!")
    print("="*50)

if __name__ == "__main__":
    # 测试正常流程
    test_full_workflow()
    
    # 测试不同级别的急诊情况
    test_level1_emergency()
    test_level2_emergency()
    test_level4_routine()
    
    # 测试错误情况
    test_error_cases()