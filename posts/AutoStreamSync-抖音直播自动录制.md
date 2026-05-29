---
title: AutoStreamSync-抖音直播自动录制
date: 2026-05-03 19:03:54
tags:
---

做了一个小工具：AutoStreamSync，它的主要用途很简单，就是自动监测抖音直播间，并在直播开始后把直播内容录制到本地。

<img src="https://gitee.com/wenswuu/pictures/raw/master/20260504225521471.webp" alt="image-20260504225510718" style="zoom:67%;" />

> 主要是前几天无聊的时候想看圆圆直播，但又懒得守着她直播，于是就整了一个，勉强可用，但仍存在一些小问题，如录制时间的bug，但应该不会改了。

- [项目地址](https://github.com/reveryday/AutoStreamSync)

- [下载地址：GitHub Releases](https://github.com/reveryday/AutoStreamSync/releases/latest)

## 它能做什么

AutoStreamSync 是一个 Windows 桌面工具。使用时只需要填写抖音直播间地址，设置保存目录和检查间隔，程序就会自动等待直播开播。检测到直播流后，它会开始录制，并把文件保存到本地。

目前主要功能包括：

- 支持同时监测多个抖音直播间
- 支持未开播时自动等待和重试
- 支持开播后自动录制
- 支持固定时长录制
- 提供简单的桌面界面
- 可以直接下载压缩包使用

## 怎么使用

普通用户不需要安装 Python，也不需要克隆源码。直接进入项目的 Release 页面下载最新[压缩包](https://github.com/reveryday/AutoStreamSync/releases/latest)，下载后解压，运行：

```text
AutoStreamSyncApp.exe
```

然后在界面里添加直播间地址，保存配置，点击开始录制即可。

## 适合什么场景

这个工具适合用来保存自己有权限录制的直播内容，比如自己的直播、授权存档的直播，或者需要做本地备份的直播素材。

录制文件默认会保存在 `downloads/` 目录，运行日志会保存在 `logs/` 目录。如果需要长时间等待直播开播，可以把检查间隔和最大失败次数调大一些。

## 说明

AutoStreamSync 只是一个本地直播录制工具。使用时请遵守相关平台规则，并只录制自己有权保存的内容。
