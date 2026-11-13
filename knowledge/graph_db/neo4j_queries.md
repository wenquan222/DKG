# DKG Neo4j 查询参考

> 打开 http://localhost:7474 登录后，复制下面的查询语句粘贴到顶部输入框，回车执行。

---

## 1. 全局概览

### 看所有节点和关系（数据少的时候用）
```cypher
MATCH (n) RETURN n
```

### 统计各类节点数量
```cypher
MATCH (n) RETURN labels(n)[0] AS 类型, count(n) AS 数量 ORDER BY 数量 DESC
```

### 统计各类关系数量
```cypher
MATCH ()-[r]->() RETURN type(r) AS 关系类型, count(r) AS 数量 ORDER BY 数量 DESC
```

---

## 2. 上层：配置空间查询

### 看某个算法的完整攻击生态
```cypher
MATCH p=(a:Algorithm {name:"AES"})-[*1..2]-() RETURN p
```

### 看某个算法有哪些攻击位置
```cypher
MATCH (a:Algorithm)-[r:has_attack_point]->(ap:AttackPoint)
RETURN a.name AS 算法, ap.name AS 攻击位置, r.is_common AS 常用
```

### 看某个设备支持什么波形采集
```cypher
MATCH (d:DeviceClass)-[r:acquires_via]->(t:TraceType)
RETURN d.name AS 设备, t.name AS 波形类型, r.is_primary AS 主要方式
```

### 看所有 works_with 关系（按confidence排序）
```cypher
MATCH (a)-[r:works_with]->(b)
RETURN a.name AS 组件A, b.name AS 组件B, r.confidence AS 置信度
ORDER BY r.confidence DESC
```

### 看预处理步骤的执行顺序
```cypher
MATCH (a)-[r:precedes]->(b)
RETURN a.name AS 前, b.name AS 后, r.is_mandatory AS 必须
```

### 看替代关系
```cypher
MATCH (a)-[r:alternative_to]->(b)
RETURN a.name AS 组件A, b.name AS 组件B, r.condition AS 条件
```

### 查询某个设备的推荐攻击路径
```cypher
MATCH (d:DeviceClass {name:"STM32F429"})-[r1:works_with]-(component)
RETURN d.name AS 设备, labels(component)[0] AS 组件类型, component.name AS 组件名, r1.confidence AS 置信度
ORDER BY r1.confidence DESC
```

---

## 3. 下层：诊断策略查询

### 看完整的诊断链（Observation → Cause → Action）
```cypher
MATCH p=(o:Observation)-[:indicates]->(c:Cause)<-[:resolves]-(a:Action)
RETURN p
```

### 列出所有诊断触发条件
```cypher
MATCH (o:Observation)
RETURN o.id AS ID, o.metric AS 指标, o.condition AS 触发条件
ORDER BY o.id
```

### 看某个观察现象的所有可能原因和修复方法
```cypher
MATCH (o:Observation {id:"diag_001"})-[i:indicates]->(c:Cause)<-[r:resolves]-(a:Action)
RETURN o.metric AS 观察指标, i.likelihood AS 可能性, c.name AS 原因, a.name AS 修复动作, a.operation AS 动作类型
```

### 按动作类型分组查看
```cypher
MATCH (a:Action)
RETURN a.operation AS 动作类型, collect(a.name) AS 动作列表, count(a) AS 数量
```

---

## 4. 跨层查询

### 上下层全部节点（分颜色显示）
```cypher
MATCH (n)
WHERE NOT n.name = "none"
RETURN n
```

### 查找某算法相关的所有知识（上层+下层）
```cypher
// 先看上层配置
MATCH p=(a:Algorithm {name:"AES"})-[*1..2]-() RETURN p
UNION
// 再看下层诊断
MATCH p=(o:Observation)-[:indicates]->(c:Cause)<-[:resolves]-(a:Action) RETURN p
```

---

## 5. 数据维护

### 清空所有数据（重新导入前用）
```cypher
MATCH (n) DETACH DELETE n
```

### 删除某个孤立节点
```cypher
MATCH (n {name:"none"}) DETACH DELETE n
```

### 查看孤立节点（没有任何关系的节点）
```cypher
MATCH (n) WHERE NOT (n)--() RETURN n
```
