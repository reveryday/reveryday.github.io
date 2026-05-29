---
title: Git
date: 2026-05-25 14:55:10
tags:
---

git典型工作流：

```
工作区（Working Directory）
        ↓
暂存区（Stage / Index）
        ↓
本地仓库（Local Repository）
        ↓
远程仓库（Remote Repository）
```

### Git本地操作

将一个文件夹变成Git仓库：

```bash
git init 
```

用`ls -la`查看所有文件会发现在执行完上面的命令后，文件夹下多了一个名为`.git`的隐藏文件夹，这个就是本地的Git版本仓库。通过`git add`可以将指定的文件或所有文件添加到暂存区：

```bash
git add <file>
git add .
```

查看工作区、暂存区和本地仓库的状态：

```bash
git status
```

如果希望用暂存区的内容恢复工作区：

```bash
git restore <file>
git restore .
```

第一次使用Git，需要配置用户名和邮箱，然后才能将代码提交到仓库：

```bash
git config --global user.name "jackfrued"
git config --global user.email "jackfrued@126.com"
```

可以用`git config --list`来查看Git的配置信息。

将暂存区的内容纳入本地仓库：

```bash
git commit -m '本次提交的说明'
```

通过`git log`查看每次提交对应的日志：

```bash
git log
git log --graph --oneline --abbrev-commit
```

### Git远程操作

拥有了Git服务器之后，就可以通过Git的远程操作将自己的工作成果推到服务器的仓库中，也可以将他人的工作成果从服务器仓库更新到本地。可以找到仓库的地址（URL），如果配置了SSH Key就使用SSH方式访问仓库，否则就用HTTPS方式，后者需要在进行远程操作时提供用户名和口令。

添加远程仓库：

```bash
git remote add origin git@gitee.com:jackfrued/python.git
```

将本地代码推送到远程仓库：

```bash
git push -u origin master:master
```

从远程仓库取回代码：

```bash
git fetch origin  # 只抓取不合并，获取远程仓库的最新代码
git pull origin main/master # 抓取+合并
git pull --rebase origin main # 抓取并使用变基合并
```

将main分支内容合并到当前分支：

```bash
git fetch origin # 获取远程仓库的最新代码
git checkout your_branch
git rebase main
```

### Git分支操作

创建名为`dev` 的分支并切换到该分支：

```bash
git branch <branch-name>
git switch <branch-name>
```

分支合并：

```bash
git switch master
git merge --no-ff dev
```

分支变基：

```bash
git merge --no-ff dev
```

### Git版本管理

```bash
git log --oneline # 查找目标版本id
git reset --hard a1b2c3d # 版本回溯
```

