---
title: Obisidian多端同步
date: 2025-09-22 12:46:48
tags: Tool&Configuration
---

之前用过Notion做笔记，但Notion的界面让我觉得很难受，而且似乎对markdown语法的渲染效果不是很好。所以最近又搬到了Obisidian上，Obisidian的界面就看着舒服得多，且由于Obisidian的笔记存储在本地，运行起来非常流畅，但也因此出现了一个问题：怎么实现笔记的多端同步？

### win端同步到坚果云

其实Obisidian同步也就是要同步整个笔记文件夹，首先需要把Windows本地的文件传到坚果云。注册一个坚果云账号，然后设置好本地同步即可：

<img src="https://gitee.com/wenswuu/pictures/raw/master/20250922125442019.webp" alt="image-20250922125435691" style="zoom:67%;" />

>from维基百科:**基于Web的分布式编写和版本控制**（英语：**W**eb-based **D**istributed **A**uthoring and **V**ersioning，缩写：**WebDAV**）是[超文本传输协议](https://zh.wikipedia.org/wiki/超文本传输协议)（HTTP）的扩展，有利于用户间协同编辑和管理存储在[万维网](https://zh.wikipedia.org/wiki/万维网)服务器文档。WebDAV由[互联网工程任务组](https://zh.wikipedia.org/wiki/互联网工程任务组)的工作组在[RFC](https://zh.wikipedia.org/wiki/RFC) [4918](https://datatracker.ietf.org/doc/html/rfc4918)中定义。
>

### Android端：坚果云+FolderSync

1. 坚果云网页端账户信息>安全选项>添加应用：用于授权第三方应用利用 WebDAV 协议访问团队的文件。

   <img src="https://gitee.com/wenswuu/pictures/raw/master/20250922130041776.webp" alt="image-20250922130037909" style="zoom:67%;" />

2. Android端基于FolderSync实现手动同步，相关设置如下（可根据自己的需求自定义）：

   <img src="https://gitee.com/wenswuu/pictures/raw/master/20250922130730068.webp" style="zoom:20%;" />

### Ipad端：坚果云+Remotely Save

1. ipad打开Obisidian选择新建一个库，库的名称需要跟win端一致，安装并启用Remotely Save插件:

   <img src="https://gitee.com/wenswuu/pictures/raw/master/20250922131400639.webp" alt="IMG_2138" style="zoom: 33%;" />

2. 在Remotely Save设置中选择远程服务为Webdav，并配置相关信息：

   <img src="https://gitee.com/wenswuu/pictures/raw/master/20250922131946062.webp" alt="IMG_2139" style="zoom: 33%;" />

   配置完成后点击左侧的同步即可从坚果云上抓取笔记。

### Obisidian的问题

- 代码块的显示似乎有些怪怪的，在Typora上编辑的Markdown文件在Obisidian无法很好的显示；

- ios端同步的问题；

  <img src="https://gitee.com/wenswuu/pictures/raw/master/20251021125134190.webp" alt="IMG_2158" style="zoom:30%;" />

