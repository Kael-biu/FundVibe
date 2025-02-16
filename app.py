from flask import Flask, render_template, request, redirect, url_for, send_file, Response
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import os
import base64
from pathlib import Path
import tempfile


app=Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
app.config['MPL_TEMP_DIR']=tempfile.mkdtemp()
os.environ['MPLCONFIGDIR']=app.config['MPL_TEMP_DIR']

# 禁用静态文件缓存（Vercel无本地存储）
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/',methods=['GET','POST'])
def index():
    if request.method=='POST':
        #处理上传的文件
        file=request.files['file']
        if file and file.filename.endswith('.xlsx'):
            # 内存处理Excel文件
            in_memory_file = io.BytesIO()
            file.save(in_memory_file)
            in_memory_file.seek(0)

            # 存储到临时目录（内存中）
            temp_path = Path(app.config['UPLOAD_FOLDER']) / 'user_data.xlsx'
            with open(temp_path, 'wb') as f:
                f.write(in_memory_file.read())

            return redirect(url_for('analyze'))
    return render_template('upload.html')

@app.route('/analyze')
def analyze():
    try:
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

        # 生成图表并转为Base64（替代保存到本地）
        img_buffer1 = io.BytesIO()
        df['累计收益率'].plot(title='累计收益率曲线')
        plt.tight_layout()
        plt.savefig(img_buffer1, format='png')
        plt.close()
        plot_data1 = base64.b64encode(img_buffer1.getvalue()).decode()

        img_buffer2 = io.BytesIO()
        df['单位净值'].plot(title='净值走势图')
        plt.tight_layout()
        plt.savefig(img_buffer2, format='png')
        plt.close()
        plot_data2 = base64.b64encode(img_buffer2.getvalue()).decode()

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
                               plot_data1=plot_data1,
                               plot_data2=plot_data2)
    except Exception as e:
        return f"分析错误：{str(e)}",500
@app.route('/download_csv')
def download_csv():
    temp_path = Path(app.config['UPLOAD_FOLDER']) / 'user_data.xlsx'
    df = pd.read_excel(temp_path)
    output = io.StringIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')
    output.seek(0)
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=analysis.csv'}
    )

@app.route('/download_excel')
def download_excel():
    temp_path = Path(app.config['UPLOAD_FOLDER']) / 'user_data.xlsx'
    df = pd.read_excel(temp_path)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='analysis.xlsx'
    )
