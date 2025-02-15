from flask import Flask, render_template, request, redirect, url_for, send_file, Response
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import io
from pathlib import Path
import tempfile

app=Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir() # 临时目录
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/',methods=['GET','POST'])
def index():
    if request.method=='POST':
        #处理上传的文件
        file=request.files['file']
        if file and file.filename.endswith('.xlsx'):
            filename=Path(app.config['UPLOAD_FOLDER']) / 'user_data.xlsx'
            file.save(filename)
            return redirect(url_for('analyze'))
    return render_template('upload.html')

@app.route('/analyze')
def analyze():
    # 读取用户上传的数据
    df=pd.read_excel(Path(app.config['UPLOAD_FOLDER']) / 'user_data.xlsx')

    #执行分析逻辑（复用之前的代码）
    df['日期'] = pd.to_datetime(df['日期'],format='%Y%m%d', errors='coerce')   #转为datetime类型
    df['日收益率'] = df['单位净值'].pct_change()  # pct_change()用来计算相邻数据的百分比变化（今日净值/昨日净值-1）
    df['累计收益率'] = (1 + df['日收益率']).cumprod() - 1
    df=df.sort_values('日期') #按日期排序
    df.set_index('日期', inplace=True)

    #关键指标计算
    annual_return = df['日收益率'].mean() * 252  # 简单平均法
    max_drawdown = (df['单位净值']/df['单位净值'].cummax()-1).min()

    #生成收益曲线图
    plt.rcParams['font.sans-serif'] = ['SimHei']  # windows系统黑体
    plt.rcParams['axes.unicode_minus'] = False

    plot_path1 = BASE_DIR / 'static' / 'images' / 'cumulative_return.png'
    os.makedirs(os.path.dirname(plot_path1),exist_ok=True)
    plt.figure(figsize=(10,4))
    df['累计收益率'].plot(title='用户数据累计收益率')  # 直接绘制列
    plt.xlabel('日期')
    plt.ylabel('累计收益率')
    plt.savefig(plot_path1)

    #生成净值走势图
    plot_path2 = BASE_DIR / 'static' / 'images' / 'net_value_trend.png'
    plt.figure(figsize=(10, 4))
    df['单位净值'].plot(title='Fund Net Value Trend')
    plt.savefig(plot_path2)
    plt.close()

    #准备Echarts数据
    dates=df.index.strftime('%Y-%m-%d').tolist()
    values=df['单位净值'].tolist()
    # df = df.reset_index()
    df_reset=df.reset_index().rename(columns={'index':'日期'})
    table_data = df_reset.head(10).to_dict('records')

    return render_template('result.html',
                           table_data=table_data,
                           annual_return=f"{annual_return:.2%}",
                           max_drawdown=f"{max_drawdown:.2%}",
                           dates=dates,
                           values=values,
                           plot_path1=plot_path1,
                           plot_path2=plot_path2)
@app.route('/download_csv')
def download_csv():
    # 读取用户上传的数据并执行分析逻辑
    df = pd.read_excel(Path(app.config['UPLOAD_FOLDER']) / 'user_data.xlsx')
    df['日期'] = pd.to_datetime(df['日期'], format='%Y%m%d', errors='coerce')
    df['日收益率'] = df['单位净值'].pct_change()
    df['累计收益率'] = (1 + df['日收益率']).cumprod() - 1
    df = df.sort_values('日期')
    df.set_index('日期', inplace=True)

    # 将分析结果保存为 CSV 文件
    output = io.StringIO()
    df.to_csv(output, index=True, encoding='utf-8-sig')
    output.seek(0)
    return Response(output, mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=analysis_data.csv"})

@app.route('/download_excel')
def download_excel():
    # 读取用户上传的数据并执行分析逻辑
    df = pd.read_excel(Path(app.config['UPLOAD_FOLDER']) / 'user_data.xlsx')
    df['日期'] = pd.to_datetime(df['日期'], format='%Y%m%d', errors='coerce')
    df['日收益率'] = df['单位净值'].pct_change()
    df['累计收益率'] = (1 + df['日收益率']).cumprod() - 1
    df = df.sort_values('日期')
    df.set_index('日期', inplace=True)

    # 将分析结果保存为 Excel 文件
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=True, sheet_name='Sheet1')
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='analysis_data.xlsx')

# if __name__ =='__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port)