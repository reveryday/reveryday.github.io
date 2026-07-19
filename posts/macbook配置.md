---
title: Macbook环境配置
date: 2026-07-16 14:10:51
tags:
---

App

- Typora - Markdown
- Piclist
- [Foxit PDF Reader](https://www.foxitsoftware.cn/pdf-reader/)
- LinearMouse
- Koodo Reader
- draw.io
- xmind
- AppCleaner
- LocalSend
- 坚果云

环境配置：

- brew（Homebrew）- 软件包管理器：类似于 Linux 里的 `apt`、`yum`，或者 Windows 里的 `winget/choco`。

- Multipass ：由 Canonical推出的轻量级虚拟机工具，可在电脑上快速创建、运行 Ubuntu Linux 虚拟机。

  ```
  Mac macOS
  │
  └── Multipass
        │
        └── Ubuntu Linux虚拟机
               │
               ├── gcc
               ├── gfortran
               ├── Python
  ```

  可把 Mac 当前用户的主目录（`~`）共享给 Multipass 里的 Ubuntu，并挂载到 Ubuntu 的 `/home/ubuntu/mac` 目录：

  ```bash
  multipass mount ~ linux:/home/ubuntu/mac
  ```

### Github配置

1.登录Github - 登录身份。

生成密钥：

```shell
ssh-keygen -t ed25519 -C "你的GitHub邮箱"
```

添加公钥到GitHub后测试连接：

```shell
ubuntu@linux:~$ ssh -T git@github.com
Hi Wens-Wu! You've successfully authenticated, but GitHub does not provide shell access.
```

如上面这样则ssh连接成功。

2.git 设置独立用户名邮箱 - 提交身份。

```
git config --global user.name "github账号名字"
git config --global user.email "github账号邮箱"
git config --list
```

可在mac与Multipass Ubuntu下分别连接不同的Github账号：

```
Mac
 ├── SSH key A
 └── git identity A

Ubuntu
 ├── SSH key B
 └── git identity B
```



















