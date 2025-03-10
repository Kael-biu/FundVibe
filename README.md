# FundVibe - 基金数据分析平台

## 🌟 项目简介
FundVibe 是一个基于 Flask 的基金数据分析平台，支持用户上传历史净值数据 Excel 文件，自动计算关键指标并生成可视化图表。核心功能包括：
- 年化收益率计算
- 最大回撤分析
- 累计收益曲线与净值走势图
- 数据导出（CSV/Excel）
- 响应式 Web 界面

## 🚀 功能亮点
1. **多图表展示**：同时提供 Matplotlib 静态图和 ECharts 动态交互图表
2. **数据验证**：自动处理日期格式错误
3. **内存优化**：基于临时文件系统处理大文件
4. **多格式导出**：支持 CSV 和 Excel 两种下载格式
5. **云端部署**：内置 Vercel 部署配置

## 📦 项目结构
.
├── app.py # 主应用程序
├── requirements.txt # 依赖清单
├── templates/
│ ├── result.html # 分析结果页面
│ └── upload.html # 文件上传页面
├── static/
│ ├── css/
│ ├── js/
│ └── images/
└── vercel.json # Vercel 部署配置

## 🛠️ 安装与运行
1. **克隆项目**
```bash
git clone https://github.com/Kael-biu/FundVibe.git
cd FundVibe
2.**创建虚拟环境（推荐)
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
3.安装依赖
pip install -r requirements.txt
4.运行应用
python app.py

访问 http://localhost:5000 上传文件

📊 技术栈
后端：Python 3.10 + Flask
数据处理：Pandas
可视化：Matplotlib + ECharts

⚠️ 注意事项
数据格式要求：Excel 文件必须包含 "日期" 和 "单位净值" 列
日期格式支持：%Y%m%d 或 %Y-%m-%d
生产环境建议：
在 app.py 中设置 debug=False
配置反向代理（如 Nginx）
使用环境变量管理敏感信息
