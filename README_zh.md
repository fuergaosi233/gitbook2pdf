<h1 align="center">Welcome to Gitbook2pdf 👋</h1>

<p>
  <a href="https://twitter.com/fuergaosi" target="_blank">
    <img alt="Twitter: fuergaosi" src="https://img.shields.io/twitter/follow/fuergaosi.svg?style=social" />
  </a>
</p>

> 简洁易用地将`gitbook`站点转换为`pdf`的工具

### 🏠 [Homepage](https://github.com/fuergaosi233/gitbook2pdf)

[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[English](./README.md) [中文](./README_zh.md)

## 特性

- 异步抓取
  使用 `aiohttp` 进行抓取
  能在几秒内完成对整个站点地抓取

- 生成的文本可以进行复制
  ![](./screenshots/copy-feature.png)
- 保存原目录结构
  ![](./screenshots/index.png)

- 保存原有的超链接

![](./screenshots/link-feature.png)

- 保存原有站点的格式（使用 js 渲染生成的无法抓取 🤷‍♂️
- 极小的存储空间占用， 800 页的 pdf 文件只占用 4.6mb

### 示例文件

[KubernetesHandbook.pdf](http://cdn2.xhyuan.co/KubernetesHandbook.pdf)

## 安装

### 请注意!

**因为它需要使用 `weasyprint` 来生成 `pdf` ，但是 `pip`无 法完成`weasyprint`的安装，因此您需要手动安装它。**
这是 `weasyprint` 的 [安装指南](https://weasyprint.readthedocs.io/en/latest/install.html#linux)
如果你不想进行依赖安装 你可以使用由 `soulteary` 提供的 [docker image](https://github.com/soulteary/docker-gitbook-pdf-generator)

```sh
pip install -r requirements.txt
```

## 使用

```sh
python gitbook.py {url}
```

## 运行测试

```sh
python gitbook.py http://self-publishing.ebookchain.org
```

## 定制

生成的 `pdf` 风格取决于`css`文件 如果你需要添加其他风格可以通过修改`gitbook.css`文件来实现.

## Author

👤 **fuergaosi233**

- Twitter: [@fuergaosi](https://twitter.com/fuergaosi)
  👤 **LiaoChangjiang**

## 🤝 贡献

欢迎提供`issues`, 以及`pr`。[issues page](https://github.com/fuergaosi233/gitbook2pdf/issues).

## 给点支持

如果这个工具帮到你了，那就请宁给我个 ⭐️ 口巴。

## warning⚠️

使用 `weasyprint` 来生成 pdf 文件会占用大量的内存。
所以请确保你有足够的内存空间来进行生成。
