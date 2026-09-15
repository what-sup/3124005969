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

## 安装运行依赖

项目需要 Python 3.10+。运行程序前安装运行时依赖：

```bash
python -m pip install -r requirements.txt
```

## 安装开发依赖和运行测试

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests/ -q
```

测试和性能材料：

- [测试与覆盖率报告](docs/test-report.md)；
- [性能分析与改进记录](docs/performance.md)；
- [覆盖率图](docs/coverage.svg)；

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
│   ├── design.md
│   ├── performance.md
│   ├── performance.svg
│   ├── test-report.md
│   └── coverage.svg
├── README.md
├── pytest.ini
├── requirements.txt
└── requirements-dev.txt
```

## 约束

程序不联网，不扫描目录，不读取样例目录或其他配置文件，不执行与查重无关的系统操作。
样例文件仅在通过命令行参数传入时使用。
