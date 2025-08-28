# 本文件为数据库调整文件，如果移植后数据库为空，请运行此文件
from datetime import datetime
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import sys
from app_config import DB_URI
sys.path.append('project') 

# 从模型文件中导入
from model import Department, DiseaseMapping, DiseaseSynonym

db_URI = DB_URI

def create_session():
    engine = create_engine(db_URI)
    Session = sessionmaker(bind=engine)
    return Session()

def delete_existing_ophthalmology_data(session):
    """删除所有眼科相关数据"""
    try:
        # 1. 查找所有眼科相关科室
        oph_departments = session.query(Department).filter(
            Department.name.ilike('%眼科%') | 
            Department.name.ilike('%视光%') | 
            Department.name.ilike('%眼病%') |
            Department.name.ilike('%玻璃体%') |
            Department.name.ilike('%视网膜%') |
            Department.name.ilike('%角膜%') |
            Department.name.ilike('%青光眼%') |
            Department.name.ilike('%白内障%')
        ).all()
        
        # 2. 收集这些科室的ID
        oph_dept_ids = [dept.id for dept in oph_departments]
        
        # 3. 删除相关疾病映射和同义词
        if oph_dept_ids:
            # 删除相关疾病同义词
            session.query(DiseaseSynonym).filter(
                DiseaseSynonym.mapping_id.in_(
                    session.query(DiseaseMapping.id).filter(
                        DiseaseMapping.department_id.in_(oph_dept_ids)
                    )
                )
            ).delete(synchronize_session=False)
            
            # 删除相关疾病映射
            session.query(DiseaseMapping).filter(
                DiseaseMapping.department_id.in_(oph_dept_ids)
            ).delete(synchronize_session=False)
            
            # 删除眼科相关科室
            session.query(Department).filter(
                Department.id.in_(oph_dept_ids)
            ).delete(synchronize_session=False)
        
        session.commit()
        print("成功清空所有眼科相关数据")
        return True
    except Exception as e:
        session.rollback()
        print(f"清空眼科数据时出错: {e}")
        return False

def create_ophthalmology_departments(session):
    """创建眼科专科科室"""
    oph_departments = [
        # 眼科细分科室
        {
            "name": "白内障科",
            "director": "王明阳",
            "phone": "020-1001",
            "description": "专门诊断和治疗各种类型的白内障（老年性、先天性、并发性等），进行超声乳化吸除联合人工晶体植入术"
        },
        {
            "name": "青光眼科",
            "director": "李青光",
            "phone": "020-1002",
            "description": "诊治青光眼，进行眼压监测、房角检查、视野检查，通过药物、激光和手术控制眼压"
        },
        {
            "name": "玻璃体视网膜科",
            "director": "张视网膜",
            "phone": "020-1003",
            "description": "诊治玻璃体和视网膜疾病，进行玻璃体切割手术、视网膜激光光凝术、眼内注药术"
        },
        {
            "name": "角膜与眼表疾病科",
            "director": "陈角膜",
            "phone": "020-1004",
            "description": "诊治角膜、结膜和眼睑相关疾病，进行角膜移植术、羊膜移植术、翼状胬肉切除术"
        },
        {
            "name": "眼视光学科",
            "director": "赵视光",
            "phone": "020-1005",
            "description": "解决屈光不正问题，提供医学验光配镜和屈光手术（全飞秒SMILE、半飞秒LASIK、ICL）"
        },
        {
            "name": "眼整形与眼眶病科",
            "director": "孙整形",
            "phone": "020-1006",
            "description": "诊治眼眶和眼睑的疾病，进行眼眶肿瘤切除术、眼眶骨折修复术、眼睑整形术"
        },
        {
            "name": "斜视与小儿眼科",
            "director": "周小儿",
            "phone": "020-1007",
            "description": "专门诊治儿童眼病和斜视问题，包括弱视、儿童屈光不正、婴幼儿泪道疾病等"
        },
        {
            "name": "眼外伤科",
            "director": "吴外伤",
            "phone": "020-1008",
            "description": "紧急处理各种机械性、化学性眼外伤，进行眼球穿孔伤缝合、眼内异物取出等急诊手术"
        },
        {
            "name": "葡萄膜炎与免疫性眼病科",
            "director": "郑葡萄",
            "phone": "020-1009",
            "description": "诊治葡萄膜炎和与其他全身免疫系统疾病相关的眼部病变"
        },
        {
            "name": "神经眼科",
            "director": "冯神经",
            "phone": "020-1010",
            "description": "诊治与神经系统相关的视觉通路疾病，包括视神经炎、缺血性视神经病变等"
        },
        
        # 相关协作科室
        {
            "name": "内分泌科",
            "director": "钱内分泌",
            "phone": "020-2001",
            "description": "糖尿病等内分泌疾病治疗，协作处理糖尿病性视网膜病变等眼病"
        },
        {
            "name": "风湿免疫科",
            "director": "钱风湿",
            "phone": "020-2002",
            "description": "免疫系统疾病治疗，协作处理免疫性眼病"
        },
        {
            "name": "神经内科",
            "director": "孙神经内",
            "phone": "020-2003",
            "description": "神经系统疾病诊疗，协作处理神经眼科疾病"
        }
    ]
    
    dept_map = {}
    for dept_data in oph_departments:
        # 检查科室是否已存在
        existing = session.query(Department).filter(
            func.lower(Department.name) == func.lower(dept_data["name"])
        ).first()
        
        if existing:
            dept_map[dept_data["name"]] = existing.id
            print(f"科室已存在: {dept_data['name']}")
        else:
            new_dept = Department(
                name=dept_data["name"],
                director=dept_data["director"],
                phone=dept_data["phone"],
                description=dept_data["description"]
            )
            session.add(new_dept)
            session.flush()
            dept_map[dept_data["name"]] = new_dept.id
            print(f"创建科室: {dept_data['name']}")
    
    session.commit()
    print("眼科科室创建完成")
    return dept_map

def create_disease_mappings(session, dept_map):
    """创建疾病-科室映射关系"""
    disease_mappings = [
        # 白内障科疾病
        {"disease_name": "老年性白内障", "department": "白内障科", "confidence": 1.0},
        {"disease_name": "先天性白内障", "department": "白内障科", "confidence": 1.0},
        {"disease_name": "并发性白内障", "department": "白内障科", "confidence": 1.0},
        {"disease_name": "外伤性白内障", "department": "白内障科", "confidence": 1.0},
        {"disease_name": "后发性白内障", "department": "白内障科", "confidence": 1.0},
        {"disease_name": "代谢性白内障", "department": "白内障科", "confidence": 1.0},
        {"disease_name": "放射性白内障", "department": "白内障科", "confidence": 1.0},
        
        # 青光眼科疾病
        {"disease_name": "原发性开角型青光眼", "department": "青光眼科", "confidence": 1.0},
        {"disease_name": "原发性闭角型青光眼", "department": "青光眼科", "confidence": 1.0},
        {"disease_name": "继发性青光眼", "department": "青光眼科", "confidence": 1.0},
        {"disease_name": "先天性青光眼", "department": "青光眼科", "confidence": 1.0},
        {"disease_name": "青少年型开角型青光眼", "department": "青光眼科", "confidence": 1.0},
        {"disease_name": "青光眼睫状体炎综合征", "department": "青光眼科", "confidence": 1.0},
        {"disease_name": "新生血管性青光眼", "department": "青光眼科", "confidence": 1.0},
        {"disease_name": "色素性青光眼", "department": "青光眼科", "confidence": 1.0},
        
        # 玻璃体视网膜科疾病
        {"disease_name": "视网膜脱离", "department": "玻璃体视网膜科", "confidence": 1.0},
        {"disease_name": "糖尿病性视网膜病变", "department": "玻璃体视网膜科", "confidence": 1.0},
        {"disease_name": "黄斑变性", "department": "玻璃体视网膜科", "confidence": 1.0},
        {"disease_name": "黄斑前膜", "department": "玻璃体视网膜科", "confidence": 1.0},
        {"disease_name": "黄斑裂孔", "department": "玻璃体视网膜科", "confidence": 1.0},
        {"disease_name": "玻璃体积血", "department": "玻璃体视网膜科", "confidence": 1.0},
        {"disease_name": "视网膜静脉阻塞", "department": "玻璃体视网膜科", "confidence": 1.0},
        {"disease_name": "视网膜动脉阻塞", "department": "玻璃体视网膜科", "confidence": 1.0},
        {"disease_name": "视网膜色素变性", "department": "玻璃体视网膜科", "confidence": 1.0},
        {"disease_name": "视网膜血管炎", "department": "玻璃体视网膜科", "confidence": 1.0},
        
        # 角膜与眼表疾病科
        {"disease_name": "细菌性角膜炎", "department": "角膜与眼表疾病科", "confidence": 1.0},
        {"disease_name": "病毒性角膜炎", "department": "角膜与眼表疾病科", "confidence": 1.0},
        {"disease_name": "真菌性角膜炎", "department": "角膜与眼表疾病科", "confidence": 1.0},
        {"disease_name": "棘阿米巴角膜炎", "department": "角膜与眼表疾病科", "confidence": 1.0},
        {"disease_name": "角膜溃疡", "department": "角膜与眼表疾病科", "confidence": 1.0},
        {"disease_name": "干眼症", "department": "角膜与眼表疾病科", "confidence": 1.0},
        {"disease_name": "翼状胬肉", "department": "角膜与眼表疾病科", "confidence": 1.0},
        {"disease_name": "角膜外伤", "department": "角膜与眼表疾病科", "confidence": 1.0},
        {"disease_name": "圆锥角膜", "department": "角膜与眼表疾病科", "confidence": 1.0},
        {"disease_name": "角膜营养不良", "department": "角膜与眼表疾病科", "confidence": 1.0},
        {"disease_name": "角膜变性", "department": "角膜与眼表疾病科", "confidence": 1.0},
        {"disease_name": "大泡性角膜病变", "department": "角膜与眼表疾病科", "confidence": 1.0},
        
        # 眼视光学科
        {"disease_name": "近视", "department": "眼视光学科", "confidence": 1.0},
        {"disease_name": "远视", "department": "眼视光学科", "confidence": 1.0},
        {"disease_name": "散光", "department": "眼视光学科", "confidence": 1.0},
        {"disease_name": "老视", "department": "眼视光学科", "confidence": 1.0},
        {"disease_name": "屈光参差", "department": "眼视光学科", "confidence": 1.0},
        {"disease_name": "调节功能障碍", "department": "眼视光学科", "confidence": 1.0},
        {"disease_name": "集合不足", "department": "眼视光学科", "confidence": 1.0},
        
        # 眼整形与眼眶病科
        {"disease_name": "眼眶肿瘤", "department": "眼整形与眼眶病科", "confidence": 1.0},
        {"disease_name": "眼眶骨折", "department": "眼整形与眼眶病科", "confidence": 1.0},
        {"disease_name": "甲状腺相关眼病", "department": "眼整形与眼眶病科", "confidence": 1.0},
        {"disease_name": "上睑下垂", "department": "眼整形与眼眶病科", "confidence": 1.0},
        {"disease_name": "眼睑内翻", "department": "眼整形与眼眶病科", "confidence": 1.0},
        {"disease_name": "眼睑外翻", "department": "眼整形与眼眶病科", "confidence": 1.0},
        {"disease_name": "眼睑肿瘤", "department": "眼整形与眼眶病科", "confidence": 1.0},
        {"disease_name": "眼睑畸形", "department": "眼整形与眼眶病科", "confidence": 1.0},
        {"disease_name": "眼窝畸形", "department": "眼整形与眼眶病科", "confidence": 1.0},
        {"disease_name": "泪囊炎", "department": "眼整形与眼眶病科", "confidence": 1.0},
        {"disease_name": "泪道阻塞", "department": "眼整形与眼眶病科", "confidence": 1.0},
        
        # 斜视与小儿眼科
        {"disease_name": "共同性内斜视", "department": "斜视与小儿眼科", "confidence": 1.0},
        {"disease_name": "共同性外斜视", "department": "斜视与小儿眼科", "confidence": 1.0},
        {"disease_name": "麻痹性斜视", "department": "斜视与小儿眼科", "confidence": 1.0},
        {"disease_name": "弱视", "department": "斜视与小儿眼科", "confidence": 1.0},
        {"disease_name": "儿童屈光不正", "department": "斜视与小儿眼科", "confidence": 1.0},
        {"disease_name": "婴幼儿泪道阻塞", "department": "斜视与小儿眼科", "confidence": 1.0},
        {"disease_name": "先天性眼球震颤", "department": "斜视与小儿眼科", "confidence": 1.0},
        {"disease_name": "婴幼儿视网膜病变", "department": "斜视与小儿眼科", "confidence": 1.0},
        
        # 眼外伤科
        {"disease_name": "眼球穿孔伤", "department": "眼外伤科", "confidence": 1.0},
        {"disease_name": "眼内异物", "department": "眼外伤科", "confidence": 1.0},
        {"disease_name": "眼睑裂伤", "department": "眼外伤科", "confidence": 1.0},
        {"disease_name": "化学性眼烧伤", "department": "眼外伤科", "confidence": 1.0},
        {"disease_name": "热烧伤", "department": "眼外伤科", "confidence": 1.0},
        {"disease_name": "辐射性眼损伤", "department": "眼外伤科", "confidence": 1.0},
        {"disease_name": "眼球钝挫伤", "department": "眼外伤科", "confidence": 1.0},
        {"disease_name": "前房积血", "department": "眼外伤科", "confidence": 1.0},
        {"disease_name": "眼睑外伤", "department": "眼外伤科", "confidence": 1.0},
        
        # 葡萄膜炎与免疫性眼病科
        {"disease_name": "前葡萄膜炎", "department": "葡萄膜炎与免疫性眼病科", "confidence": 1.0},
        {"disease_name": "中间葡萄膜炎", "department": "葡萄膜炎与免疫性眼病科", "confidence": 1.0},
        {"disease_name": "后葡萄膜炎", "department": "葡萄膜炎与免疫性眼病科", "confidence": 1.0},
        {"disease_name": "全葡萄膜炎", "department": "葡萄膜炎与免疫性眼病科", "confidence": 1.0},
        {"disease_name": "白塞氏病眼病", "department": "葡萄膜炎与免疫性眼病科", "confidence": 1.0},
        {"disease_name": "伏格特-小柳-原田综合征", "department": "葡萄膜炎与免疫性眼病科", "confidence": 1.0},
        {"disease_name": "强直性脊柱炎相关葡萄膜炎", "department": "葡萄膜炎与免疫性眼病科", "confidence": 1.0},
        {"disease_name": "类风湿关节炎相关巩膜炎", "department": "葡萄膜炎与免疫性眼病科", "confidence": 1.0},
        {"disease_name": "交感性眼炎", "department": "葡萄膜炎与免疫性眼病科", "confidence": 1.0},
        {"disease_name": "结节病性葡萄膜炎", "department": "葡萄膜炎与免疫性眼病科", "confidence": 1.0},
        
        # 神经眼科
        {"disease_name": "视神经炎", "department": "神经眼科", "confidence": 1.0},
        {"disease_name": "缺血性视神经病变", "department": "神经眼科", "confidence": 1.0},
        {"disease_name": "视神经萎缩", "department": "神经眼科", "confidence": 1.0},
        {"disease_name": "视神经挫伤", "department": "神经眼科", "confidence": 1.0},
        {"disease_name": "视神经肿瘤", "department": "神经眼科", "confidence": 1.0},
        {"disease_name": "视交叉病变", "department": "神经眼科", "confidence": 1.0},
        {"disease_name": "视路病变", "department": "神经眼科", "confidence": 1.0},
        {"disease_name": "瞳孔运动障碍", "department": "神经眼科", "confidence": 1.0},
        {"disease_name": "核间性眼肌麻痹", "department": "神经眼科", "confidence": 1.0},
        {"disease_name": "眼肌麻痹", "department": "神经眼科", "confidence": 1.0},
        
        # 急诊分级相关眼病
        {"disease_name": "急性闭角型青光眼", "department": "青光眼科", "confidence": 1.0, "is_emergency": True},
        {"disease_name": "视网膜中央动脉阻塞", "department": "玻璃体视网膜科", "confidence": 1.0, "is_emergency": True},
        {"disease_name": "眼内炎", "department": "葡萄膜炎与免疫性眼病科", "confidence": 1.0, "is_emergency": True},
        {"disease_name": "眼球破裂伤", "department": "眼外伤科", "confidence": 1.0, "is_emergency": True},
        {"disease_name": "化学性眼烧伤", "department": "眼外伤科", "confidence": 1.0, "is_emergency": True},
        {"disease_name": "玻璃体积血", "department": "玻璃体视网膜科", "confidence": 1.0, "is_emergency": True},
        {"disease_name": "视网膜脱离", "department": "玻璃体视网膜科", "confidence": 1.0, "is_emergency": True},
        {"disease_name": "角膜溃疡穿孔", "department": "角膜与眼表疾病科", "confidence": 1.0, "is_emergency": True},
        
        # 跨科室协作疾病
        {"disease_name": "糖尿病性白内障", "department": "内分泌科", "confidence": 0.9},
        {"disease_name": "高血压视网膜病变", "department": "内科", "confidence": 0.8},
        {"disease_name": "视神经炎", "department": "神经内科", "confidence": 0.85},
        {"disease_name": "甲状腺相关眼病", "department": "内分泌科", "confidence": 0.9},
        {"disease_name": "过敏性结膜炎", "department": "皮肤科", "confidence": 0.7},
        {"disease_name": "鼻泪管阻塞", "department": "耳鼻喉科", "confidence": 0.75}
    ]
    
    disease_map = {}  # 存储疾病名称到映射ID的对应关系
    added_count = 0
    
    for dm in disease_mappings:
        dept_name = dm["department"]
        if dept_name not in dept_map:
            print(f"警告: 找不到科室 '{dept_name}'，跳过疾病 '{dm['disease_name']}'")
            continue
            
        # 创建疾病映射
        mapping = DiseaseMapping(
            disease_name=dm["disease_name"],
            department_id=dept_map[dept_name],
            confidence=dm["confidence"]
        )
        
        # 添加急诊标记（如果存在）
        if "is_emergency" in dm and dm["is_emergency"]:
            # 实际项目中可以添加额外字段，这里简化处理
            # mapping.is_emergency = True
            pass
            
        session.add(mapping)
        session.flush()
        disease_map[dm["disease_name"]] = mapping.id
        added_count += 1
        print(f"添加疾病映射: {dm['disease_name']} -> {dept_name}")
    
    session.commit()
    print(f"\n成功添加 {added_count} 条疾病映射")
    return disease_map

def create_disease_synonyms(session, disease_map):
    """创建疾病同义词"""
    synonyms_data = [
        # 白内障同义词
        {"disease_name": "老年性白内障", "synonym": "年龄相关性白内障", "score": 0.98},
        {"disease_name": "老年性白内障", "synonym": "老年白内障", "score": 0.97},
        {"disease_name": "先天性白内障", "synonym": "发育性白内障", "score": 0.95},
        {"disease_name": "并发性白内障", "synonym": "继发性白内障", "score": 0.96},
        
        # 青光眼同义词
        {"disease_name": "原发性开角型青光眼", "synonym": "慢性开角型青光眼", "score": 0.97},
        {"disease_name": "原发性开角型青光眼", "synonym": "POAG", "score": 0.98},
        {"disease_name": "原发性闭角型青光眼", "synonym": "急性闭角型青光眼", "score": 0.96},
        {"disease_name": "原发性闭角型青光眼", "synonym": "急性青光眼", "score": 0.95},
        {"disease_name": "青光眼睫状体炎综合征", "synonym": "Posner-Schlossman综合征", "score": 0.95},
        {"disease_name": "新生血管性青光眼", "synonym": "NVG", "score": 0.97},
        
        # 视网膜疾病同义词
        {"disease_name": "糖尿病性视网膜病变", "synonym": "糖网症", "score": 0.99},
        {"disease_name": "糖尿病性视网膜病变", "synonym": "DR", "score": 0.98},
        {"disease_name": "黄斑变性", "synonym": "老年性黄斑变性", "score": 0.98},
        {"disease_name": "黄斑变性", "synonym": "AMD", "score": 0.97},
        {"disease_name": "黄斑变性", "synonym": "ARMD", "score": 0.95},
        {"disease_name": "视网膜中央动脉阻塞", "synonym": "眼中风", "score": 0.96},
        {"disease_name": "视网膜中央动脉阻塞", "synonym": "CRAO", "score": 0.97},
        {"disease_name": "视网膜中央静脉阻塞", "synonym": "CRVO", "score": 0.97},
        {"disease_name": "玻璃体积血", "synonym": "玻璃体出血", "score": 0.99},
        
        # 角膜疾病同义词
        {"disease_name": "翼状胬肉", "synonym": "攀睛", "score": 0.95},
        {"disease_name": "翼状胬肉", "synonym": "胬肉攀睛", "score": 0.93},
        {"disease_name": "干眼症", "synonym": "干燥性角结膜炎", "score": 0.97},
        {"disease_name": "干眼症", "synonym": "干眼病", "score": 0.98},
        {"disease_name": "干眼症", "synonym": "KCS", "score": 0.96},
        {"disease_name": "圆锥角膜", "synonym": "KC", "score": 0.97},
        {"disease_name": "细菌性角膜炎", "synonym": "细菌性角膜溃疡", "score": 0.98},
        
        # 眼视光同义词
        {"disease_name": "近视", "synonym": "近视眼", "score": 0.98},
        {"disease_name": "近视", "synonym": "短视", "score": 0.90},
        {"disease_name": "远视", "synonym": "远视眼", "score": 0.98},
        {"disease_name": "散光", "synonym": "散光眼", "score": 0.98},
        {"disease_name": "老视", "synonym": "老花眼", "score": 0.99},
        {"disease_name": "老视", "synonym": "老花", "score": 0.98},
        
        # 眼眶疾病同义词
        {"disease_name": "甲状腺相关眼病", "synonym": "Graves眼病", "score": 0.98},
        {"disease_name": "甲状腺相关眼病", "synonym": "TAO", "score": 0.97},
        {"disease_name": "甲状腺相关眼病", "synonym": "突眼症", "score": 0.95},
        {"disease_name": "泪囊炎", "synonym": "慢性泪囊炎", "score": 0.96},
        
        # 斜视同义词
        {"disease_name": "共同性内斜视", "synonym": "内斜视", "score": 0.97},
        {"disease_name": "共同性内斜视", "synonym": "对眼", "score": 0.90},
        {"disease_name": "共同性外斜视", "synonym": "外斜视", "score": 0.97},
        {"disease_name": "弱视", "synonym": "懒惰眼", "score": 0.92},
        
        # 神经眼科同义词
        {"disease_name": "视神经炎", "synonym": "球后视神经炎", "score": 0.96},
        {"disease_name": "视神经炎", "synonym": "视神经乳头炎", "score": 0.95},
        {"disease_name": "缺血性视神经病变", "synonym": "AION", "score": 0.97},
        
        # 其他同义词
        {"disease_name": "葡萄膜炎", "synonym": "虹膜睫状体炎", "score": 0.95},
        {"disease_name": "葡萄膜炎", "synonym": "前葡萄膜炎", "score": 0.96},
        {"disease_name": "眼内炎", "synonym": "眼内感染", "score": 0.98},
        {"disease_name": "眼内炎", "synonym": "感染性眼内炎", "score": 0.97},
        {"disease_name": "化学性眼烧伤", "synonym": "化学伤", "score": 0.96},
        {"disease_name": "眼球破裂伤", "synonym": "眼球穿通伤", "score": 0.97},
        
        # 急诊相关同义词
        {"disease_name": "急性闭角型青光眼", "synonym": "急性青光眼发作", "score": 0.98},
        {"disease_name": "视网膜中央动脉阻塞", "synonym": "视网膜动脉阻塞", "score": 0.97},
        {"disease_name": "角膜溃疡穿孔", "synonym": "角膜穿孔", "score": 0.98},
    ]
    
    added_count = 0
    for syn in synonyms_data:
        disease_name = syn["disease_name"]
        if disease_name not in disease_map:
            print(f"警告: 找不到疾病 '{disease_name}'，跳过同义词 '{syn['synonym']}'")
            continue
            
        # 检查同义词是否已存在
        existing = session.query(DiseaseSynonym).filter_by(
            mapping_id=disease_map[disease_name],
            synonym=syn["synonym"]
        ).first()
        
        if existing:
            print(f"同义词已存在: {disease_name} -> {syn['synonym']}")
            continue
            
        # 创建同义词
        synonym = DiseaseSynonym(
            mapping_id=disease_map[disease_name],
            synonym=syn["synonym"],
            similarity_score=syn["score"]
        )
        session.add(synonym)
        added_count += 1
        print(f"添加同义词: {disease_name} -> {syn['synonym']}")
    
    session.commit()
    print(f"\n成功添加 {added_count} 条同义词")
    return added_count
    """创建疾病同义词"""
    synonyms_data = [
        # 白内障同义词
        {"disease_name": "老年性白内障", "synonym": "年龄相关性白内障", "score": 0.98},
        {"disease_name": "先天性白内障", "synonym": "发育性白内障", "score": 0.95},
        
        # 青光眼同义词
        {"disease_name": "原发性开角型青光眼", "synonym": "慢性开角型青光眼", "score": 0.97},
        {"disease_name": "原发性闭角型青光眼", "synonym": "急性闭角型青光眼", "score": 0.96},
        {"disease_name": "青光眼睫状体炎综合征", "synonym": "Posner-Schlossman综合征", "score": 0.95},
        
        # 视网膜疾病同义词
        {"disease_name": "糖尿病性视网膜病变", "synonym": "糖网症", "score": 0.99},
        {"disease_name": "黄斑变性", "synonym": "老年性黄斑变性", "score": 0.98},
        {"disease_name": "黄斑变性", "synonym": "AMD", "score": 0.97},
        {"disease_name": "视网膜中央动脉阻塞", "synonym": "眼中风", "score": 0.96},
        
        # 角膜疾病同义词
        {"disease_name": "翼状胬肉", "synonym": "攀睛", "score": 0.95},
        {"disease_name": "干眼症", "synonym": "干燥性角结膜炎", "score": 0.97},
        
        # 眼视光同义词
        {"disease_name": "近视", "synonym": "近视眼", "score": 0.98},
        {"disease_name": "老视", "synonym": "老花眼", "score": 0.99},
        
        # 眼眶疾病同义词
        {"disease_name": "甲状腺相关眼病", "synonym": "Graves眼病", "score": 0.98},
        
        # 斜视同义词
        {"disease_name": "共同性内斜视", "synonym": "内斜视", "score": 0.97},
        
        # 神经眼科同义词
        {"disease_name": "视神经炎", "synonym": "球后视神经炎", "score": 0.96},
        
        # 其他同义词
        {"disease_name": "葡萄膜炎", "synonym": "虹膜睫状体炎", "score": 0.95},
        {"disease_name": "玻璃体积血", "synonym": "玻璃体出血", "score": 0.99},
    ]
    
    added_count = 0
    for syn in synonyms_data:
        disease_name = syn["disease_name"]
        if disease_name not in disease_map:
            print(f"警告: 找不到疾病 '{disease_name}'，跳过同义词 '{syn['synonym']}'")
            continue
            
        # 创建同义词
        synonym = DiseaseSynonym(
            mapping_id=disease_map[disease_name],
            synonym=syn["synonym"],
            similarity_score=syn["score"]
        )
        session.add(synonym)
        added_count += 1
        print(f"添加同义词: {disease_name} -> {syn['synonym']}")
    
    session.commit()
    print(f"\n成功添加 {added_count} 条同义词")
    return added_count

def main():
    session = create_session()
    
    try:
        print("="*50)
        print("开始眼科专科数据库重建")
        print("="*50)
        
        # 步骤1: 清空现有眼科数据
        print("\n步骤1: 清空现有眼科相关数据...")
        if not delete_existing_ophthalmology_data(session):
            print("无法继续执行，请检查错误")
            return
        
        # 步骤2: 创建眼科专科科室
        print("\n步骤2: 创建眼科专科科室...")
        dept_map = create_ophthalmology_departments(session)
        
        # 步骤3: 创建疾病-科室映射
        print("\n步骤3: 创建疾病-科室映射关系...")
        disease_map = create_disease_mappings(session, dept_map)
        
        # 步骤4: 创建疾病同义词
        print("\n步骤4: 创建疾病同义词...")
        create_disease_synonyms(session, disease_map)
        

        print("\n" + "="*50)
        print("眼科专科数据库重建成功完成!")
        print("="*50)
        
    except IntegrityError as e:
        session.rollback()
        print(f"数据库操作失败: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        session.rollback()
        print(f"重建过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


    
if __name__ == '__main__':
    main()