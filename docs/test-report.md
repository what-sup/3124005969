# 测试与覆盖率报告

## 1. 测试环境

- Python：3.11；
- 运行依赖：`requirements.txt`；
- 开发工具：`pytest==9.1.1`、`pytest-cov==7.1.0`、`ruff==0.16.7`；
- 测试配置：`pytest.ini` 只过滤 `jieba` 第三方源码产生的 `DeprecationWarning`，不屏蔽本项目警告。

## 2. 测试结果

使用开发依赖执行：

```bash
python3 -m pytest tests/ -q
```

结果：

```text
34 passed in 1.96s
```

测试按文件分组如下：

| 测试文件 | 用例数 | 覆盖内容 |
|---|---:|---|
| `test_cli_contract.py` | 1 | 三参数命令行合同、两位小数输出 |
| `test_errors.py` | 5 | 参数数量、输入缺失、编码错误、输出失败 |
| `test_file_io.py` | 6 | UTF-8、GB18030、读写异常、格式化 |
| `test_integration.py` | 4 | 空文本、标点空白、无共同 token、重复词 |
| `test_main.py` | 3 | 主函数成功、参数错误、输入错误 |
| `test_similarity.py` | 5 | 相同、正交、部分重叠、空向量、零范数 |
| `test_text_processor.py` | 5 | 规范化、分词、重复 token、无效 token、无缓存 |
| `test_tfidf.py` | 5 | 平滑 IDF、相同文档、空文档、空集合、向量数量 |
| **合计** | **34** | |

测试使用真实文件和真实子进程，不用 mock 替代核心计算路径。

## 3. 覆盖率结果

使用命令：

```bash
python3 -m pytest --cov=main --cov=plagiarism \
    --cov-report=term-missing tests/
```

结果：

| 模块 | 语句数 | 未覆盖 | 覆盖率 |
|---|---:|---:|---:|
| `main.py` | 28 | 1 | 96% |
| `plagiarism/__init__.py` | 0 | 0 | 100% |
| `plagiarism/errors.py` | 5 | 0 | 100% |
| `plagiarism/file_io.py` | 23 | 0 | 100% |
| `plagiarism/similarity.py` | 13 | 0 | 100% |
| `plagiarism/text_processor.py` | 28 | 3 | 89% |
| `plagiarism/tfidf.py` | 22 | 0 | 100% |
| **总计** | **119** | **4** | **97%** |

`main.py` 的未覆盖行是脚本入口的 `SystemExit` 行；命令行合同测试通过独立子进程实际执行该入口。`text_processor.py` 的未覆盖行是内存 tokenizer 的防御性初始化分支，不影响主路径的分词、缓存约束和错误测试。

## 4. 官方样例验收

官方目录中的 6 个文件均通过命令行接口直接运行。后 4 个文件是 HTML 页面，程序按照当前验收口径将 HTML 源码作为普通文本输入，不进行标签提取。

| 抄袭版文件 | 输出 | 退出码 | 标准错误 |
|---|---:|---:|---|
| `orig.txt` | `1.00` | 0 | 空 |
| `orig_0.8_add.txt` | `0.99` | 0 | 空 |
| `orig_0.8_del.txt` | `0.10` | 0 | 空 |
| `orig_0.8_dis_1.txt` | `0.13` | 0 | 空 |
| `orig_0.8_dis_10.txt` | `0.13` | 0 | 空 |
| `orig_0.8_dis_15.txt` | `0.13` | 0 | 空 |

答案文件均只包含一个保留两位小数的浮点数，并在测试后清理临时输出目录。

## 5. 测试设计说明

测试采用白盒和边界测试相结合：

- 以模块接口为单位验证正常路径；
- 以空输入、无共同词、零向量验证边界；
- 以缺失文件、坏编码、不可写输出和错误参数验证异常路径；
- 以子进程验证真实命令行、退出码、标准输出/错误和答案文件；
- 以临时目录验证运行时不生成 `jieba` 磁盘缓存。

覆盖率图见 [`coverage.svg`](coverage.svg)，性能材料见 [`performance.md`](performance.md)。
