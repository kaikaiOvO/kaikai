import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
from pyecharts.charts import WordCloud, Bar, Line, Scatter, Pie,TreeMap,Funnel
from pyecharts import options as opts
from streamlit.components.v1 import html
import re


#设置应用标题
st.title('交互式文本分析Web应用')
# 创建一个文本输入框，用于输入URL
url = st.text_input('输入文章URL:')
# 定义一系列图表类型供用户选择
sidebar_options = ['词云图', '柱状图', '折线图', '散点图', '瀑布图', '漏斗图', '饼图','矩形树图']
# 在侧边栏创建一个下拉选择框，让用户选择图表类型
chart_type = st.sidebar.selectbox('选择图表类型', sidebar_options)

if url:
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    # 使用BeautifulSoup解析响应文本
    soup = BeautifulSoup(response.content, 'html.parser')
    # 获取文本内容
    text = soup.text
    # 1. 移除 HTML 标签（如果存在）
    cleaned_text = re.sub(r'<.*?>', '', text)
    # 2. 去除空白字符
    cleaned_text = " ".join(cleaned_text.split())
    # 3. 去除标点和特殊字符
    punctuation = '''！ ；（ ） —— |  ：“”，、。( )-[ ]{ };:'"\,<>./?@#$%^&*_~'''
    cleaned_text = cleaned_text.translate(str.maketrans('', '', punctuation))
    # 4. 转换为小写
    cleaned_text = cleaned_text.lower()
    # 5. 去除数字
    cleaned_text = re.sub(r'\d+', '', cleaned_text)
    # 6. 设置停用词
    stop_words = {"的", "是", "在", "有", "和", "也", "了", "不", "我", "我们", ...}
    # 7. 分词并去除停用词
    words = jieba.cut(cleaned_text)
    cleaned_text = ''.join([word for word in words if word not in stop_words])  # 不使用空格连接

    # 8. 再次去除多余的空格（如果需要）
    cleaned_text = re.sub(r'\s+', '', cleaned_text)
    # 使用 jieba 库进行中文分词
    words = jieba.lcut(cleaned_text)
    # 使用 collections 库中的 Counter 工具统计词频
    word_counts = Counter(words)

    # 创建一个滑动条，用于选择最小词频
    min_freq = st.slider('最小词频', 1, 200, 5)
    # 根据最小词频过滤词汇
    freq_words = {k: v for k, v in word_counts.items() if v >= min_freq}
    # 从过滤后的词频中找出最常见的20个词并存在字典中
    top20_words = dict(Counter(freq_words).most_common(20))

    # 根据选定的图表类型绘制图表
    if chart_type == '词云图':
        wc = WordCloud()
        wc.add("", list(top20_words.items()), word_size_range=[20, 100])
        wc.set_global_opts(
            title_opts=opts.TitleOpts(title="词云图"),
        )
        wc_html = wc.render_embed()
        st.components.v1.html(wc_html, width=900, height=600)
    elif chart_type == '柱状图':
        bar = Bar()
        bar.add_xaxis(list(top20_words.keys()))
        bar.add_yaxis("", list(top20_words.values()))
        bar.set_global_opts(
            title_opts=opts.TitleOpts(title="柱状图"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-30))
        )
        bar_html = bar.render_embed()
        st.components.v1.html(bar_html, width=900, height=600)

    elif chart_type == '折线图':
        line = Line()
        line.add_xaxis(list(top20_words.keys()))
        line.add_yaxis("", list(top20_words.values()))
        line.set_global_opts(
            title_opts=opts.TitleOpts(title="折线图"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-30))
        )
        line_html = line.render_embed()
        st.components.v1.html(line_html, width=900, height=600)

    elif chart_type == '饼图':
        pie = Pie()
        # 添加数据项和百分比的显示
        pie.add(
            series_name="",
            data_pair=list(top20_words.items()),
            radius=["20%", "75%"],  # 可以调整饼图的内外半径来改变饼图的厚度
            label_opts=opts.LabelOpts(
                formatter="{b}: {d}%"  # 格式化标签显示为 “标签: 百分比”
            )
        )
        pie.set_global_opts(
            title_opts=opts.TitleOpts(title="饼图"),  # 可以根据需要设置标题
            legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="1%")  # 调整图例位置
        )
        pie_html = pie.render_embed()
        st.components.v1.html(pie_html, width=900, height=600)

    elif chart_type == '散点图':
        scatter = Scatter()
        scatter.add_xaxis(list(top20_words.keys()))
        scatter.add_yaxis("", list(top20_words.values()))
        scatter.set_global_opts(
            title_opts=opts.TitleOpts(title="散点图"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-30))
        )
        scatter_html = scatter.render_embed()
        st.components.v1.html(scatter_html, width=900, height=600)

    elif  chart_type == '瀑布图':
        bar = Bar(init_opts=opts.InitOpts(renderer='canvas'))
        bar.add_xaxis(list(top20_words.keys()))
        bar.add_yaxis("", list(top20_words.values()))
        # 不显示柱状图颜色标签
        bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        # 设置图表标题、坐标轴信息
        bar.set_global_opts(
            title_opts=opts.TitleOpts(title="瀑布图"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-30)),
            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}")),

            # 设置tooltip提示信息
            tooltip_opts=opts.TooltipOpts(is_show=True),

            # 设置视觉映射组件控制颜色渐变
            visualmap_opts=opts.VisualMapOpts(
                is_show=True, pos_left="10%", pos_top="30%",
                min_=min(top20_words.values()), max_=max(top20_words.values())
            )
        )
        bar_html = bar.render_embed()
        st.components.v1.html(bar_html, width=900, height=600)

    elif chart_type == '漏斗图':
        funnel = Funnel()
        funnel.add("", list(top20_words.items()))
        funnel.set_global_opts(
            title_opts=opts.TitleOpts(title="漏斗图", pos_top="20%"),  # 调整标题位置
        )
        funnel_html = funnel.render_embed()
        st.components.v1.html(funnel_html, width=900, height=600)
    elif chart_type == '矩形树图':
        treemap = TreeMap()
        treemap_data = [{"name": key, "value": value} for key, value in top20_words.items()]
        treemap.add("", treemap_data, label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        treemap.set_global_opts(title_opts=opts.TitleOpts(title="矩形树图"))
        treemap_html = treemap.render_embed()
        st.components.v1.html(treemap_html, width=900, height=600)

    #显示词汇
    st.write('词频排名前20的词汇:')
    for word, count in Counter(freq_words).most_common(20):
        st.write(f'{word}: {count}')
