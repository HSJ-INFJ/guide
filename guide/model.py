from datetime import datetime
from exts import db 

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 科室ID
    name = db.Column(db.String(100), nullable=False, unique=True)     # 科室名称
    director = db.Column(db.String(50), nullable=False)               # 负责人
    phone = db.Column(db.String(20), nullable=True)                   # 联系电话
    description = db.Column(db.Text, nullable=True)                   # 科室简介
    created_at = db.Column(db.DateTime, default=datetime.now)         # 创建时间

    def __repr__(self):
        return f"<Department {self.name}>"

class DiseaseMapping(db.Model):
    __tablename__ = 'disease_mappings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    disease_name = db.Column(db.String(200), nullable=False, index=True)  # 标准疾病名
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    confidence = db.Column(db.Float, default=1.0)  # 映射可信度
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    department = db.relationship('Department', backref='disease_mappings')
    
    def __repr__(self):
        return f"<DiseaseMapping {self.disease_name} -> {self.department.name}>"

class DiseaseSynonym(db.Model):
    __tablename__ = 'disease_synonyms'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mapping_id = db.Column(db.Integer, db.ForeignKey('disease_mappings.id'), nullable=False)
    synonym = db.Column(db.String(200), nullable=False, index=True)  # 同义词/别名
    similarity_score = db.Column(db.Float, default=1.0)  # 相似度分数
    
    mapping = db.relationship('DiseaseMapping', backref='synonyms')
