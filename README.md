# 论文查重

这是第一次个人编程作业的 Python 实现。

## 当前方案

- 使用 Python 3；
- 使用 `jieba` 进行中文分词；
- 自己实现 TF-IDF 向量计算；
- 自己实现余弦相似度；
- 程序只读取命令行传入的两个输入文件，只写入命令行传入的答案文件。

## 运行方式

```bash
python main.py <原文绝对路径> <抄袭版绝对路径> <答案文件绝对路径>
```

答案文件输出一个保留两位小数的浮点数。

## 安装依赖

```bash
python -m pip install -r requirements.txt
```

## 运行测试

```bash
python -m pytest tests/ -q
```

## 项目结构

```text
├── main.py
├── plagiarism/
│   ├── file_io.py
│   ├── text_processor.py
│   ├── tfidf.py
│   ├── similarity.py
│   └── errors.py
├── tests/
├── docs/
│   ├── PSP.md
│   └── design.md
├── README.md
└── requirements.txt
```

## 约束

程序不联网，不扫描目录，不读取样例目录或其他配置文件，不执行与查重无关的系统操作。
样例文件仅在通过命令行参数传入时使用。
