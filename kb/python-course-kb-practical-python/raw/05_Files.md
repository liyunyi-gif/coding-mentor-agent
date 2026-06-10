# 文件处理

Python 提供简洁的文件读写接口。

## 读取文件

```python
with open('file.txt', 'r') as f:
    content = f.read()
```

## 写入文件

```python
with open('output.txt', 'w') as f:
    f.write('Hello')
```

前置要求：字符串。
