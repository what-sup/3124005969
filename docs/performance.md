# 性能分析与改进记录

## 1. 测试对象与环境

- 程序入口：`main.py`；
- 输入：官方样例中的 `orig.txt` 和 `orig_0.8_add.txt`；
- 运行环境：macOS、Python 3.11、`jieba` 0.42.1；
- Python 项目使用 `cProfile`，资源测量使用 macOS 的 `/usr/bin/time -l`；这是对作业要求中 Windows 性能工具的本机等价替代；
- 所有答案文件都写入一次性临时目录，测试结束后删除。

## 2. 剖析结果

使用 `cProfile` 在同一进程中调用 `main([...])`，得到：

- 总调用数：`1,857,444`（含递归调用）；
- 剖析总耗时：`0.592` 秒；
- 主要耗时集中在 `jieba` 分词和首次构建内存词典，而不是 TF-IDF 或余弦计算。

| 函数 | 调用次数 | 累计耗时（秒） | 说明 |
|---|---:|---:|---|
| `text_processor.py:tokenize` | 2 | 0.588 | 两个输入文件的分词入口 |
| `jieba.lcut` | 2 | 0.576 | 分词主过程 |
| `_InMemoryTokenizer.initialize` | 1 | 0.489 | 首次加载内存词典 |
| `jieba.gen_pfdict` | 1 | 0.489（自身 0.394） | 解析内置词典 |
| `jieba.get_DAG` | 1,852 | 0.506 | 中文分词内部步骤 |

程序使用自定义内存初始化器，避免 `jieba` 默认生成磁盘缓存。这满足“只读命令行输入、只写命令行输出”的运行边界，但首次启动仍需解析内置词典。

## 3. 实施的改进

原来的有效 token 判断使用生成器：

```python
any(character.isalnum() for character in token)
```

改为等价的 `map` 调用：

```python
any(map(str.isalnum, token))
```

该改动不改变 token 结果，只减少 Python 层循环开销。使用两个官方纯文本样例，在同一进程中交错执行旧实现和新实现各 60 轮，并先完成词典预热：

| 实现 | 两个文件一次处理的平均耗时 |
|---|---:|
| 旧实现 | 0.035635 秒 |
| 新实现 | 0.034591 秒 |
| 变化 | -2.93% |

基准脚本同时断言两种实现产生的 token 序列完全一致。

## 4. 端到端结果

对同一对官方纯文本样例执行完整命令 10 次，所有运行均退出码为 0，答案均为 `0.99`：

| 指标 | 实测值 |
|---|---:|
| 平均耗时 | 0.272103 秒 |
| 中位数 | 0.270120 秒 |
| 最小值 | 0.266898 秒 |
| 最大值 | 0.286317 秒 |
| 单次最大常驻内存 | 100007936 字节（95.38 MiB） |

该结果低于题目规定的 5 秒和 2048 MB 限制。耗时和内存会随机器、Python 版本及依赖安装方式变化，因此表中的数值是本机实测记录，不是评测机保证值。

## 5. 样例验收范围

| 输入组合 | 结果 | 验收性质 |
|---|---:|---|
| `orig.txt` 与 `orig.txt` | `1.00` | 官方样例原样运行 |
| `orig.txt` 与 `orig_0.8_add.txt` | `0.99` | 官方样例原样运行 |
| `orig.txt` 与 `orig_0.8_del.txt` | `0.10` | HTML 源码原样作为文本输入 |
| `orig.txt` 与 `orig_0.8_dis_1.txt` | `0.13` | HTML 源码原样作为文本输入 |
| `orig.txt` 与 `orig_0.8_dis_10.txt` | `0.13` | HTML 源码原样作为文本输入 |
| `orig.txt` 与 `orig_0.8_dis_15.txt` | `0.13` | HTML 源码原样作为文本输入 |

后四个文件的首个非空内容是 `<!DOCTYPE html>`，压缩包中的对应文件也相同。按本项目的验收口径，程序直接读取这些文件内容并作为普通文本分词，不进行 HTML 解析，也不联网获取页面。

## 6. 可复现实验命令

在仓库根目录执行：

```bash
# 完整测试
PYTHONPATH=. uv run --no-project --with-requirements requirements.txt --with pytest pytest tests/ -q

# 静态分析
uv run --no-project --with-requirements requirements.txt --with ruff ruff check main.py plagiarism tests

# 剖析（将输入路径替换为本机绝对路径）
python -m cProfile -s cumulative main.py <原文绝对路径> <抄袭版绝对路径> <答案绝对路径>

# macOS 资源测量
/usr/bin/time -l python main.py <原文绝对路径> <抄袭版绝对路径> <答案绝对路径>
```

性能图见 [`performance.svg`](performance.svg)。
