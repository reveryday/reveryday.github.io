---
title: Hexo Blog Configuration
date: 2025-02-09 21:53:10
tags: Tool&Configuration
---

### 1-博客搭建：

1、安装Git，安装好后检查版本信息：

```bash
$ git --version
git version 2.47.1.windows.2
```

2、安装nodejs（Hexo是基于nodejs编写的，需安装nodejs和里面的npm工具， npm会随Node.js一起安装），安装好后需将npm的全局包路径需要添加到系统的 PATH 环境变量中（通常为：C:\Users\用户名\AppData\Roaming\npm），再检查版本信息：

```bash
$ node -v
v22.13.0
$ npm -v
10.9.2
```

3、安装hexo，全局安装：

```bash
$ npm install -g hexo-cli
```

初始化：

```bash
$ hexo init Blog
```

```bash
$ npm install

up to date in 1s

24 packages are looking for funding
  run `npm fund` for details
$ ls
_config.landscape.yml  db.json    node_modules/      package.json  scaffolds/  themes/
_config.yml            deploy.sh  package-lock.json  public/       source/
```

4、生成SSH添加到GitHub

配置 Git 的全局用户名和邮箱：

```bash
$ git config --global user.name"reveryday"
$ git config --global user.email"wenswuu@gmail.com"
```

检查是否配置成功：

```bash
$ git config --global --list
user.name=reveryday
user.email=wenswuu@gmail.com
core.autocrlf=true
```

创建SSH密钥：

```bash
$ ssh-keygen -t rsa -C "wenswuu@gmail.com"
```

在GitHub的setting中，找到SSH keys的设置选项，点击New SSH key，把 C:\Users\34001\.ssh\id_rsa.pub 里内容复制进去，查看是否成功：

```bash
$ ssh -T git@github.com
Hi reveryday! You've successfully authenticated, but GitHub does not provide shell access.
```

5、将hexo部署到GitHub

打开站点配置文件  _config.yml ，翻到最后，修改为（若default brunch是main，则应改为main）：

```yaml
deploy:
  type: git
  repo: https://github.com/reveryday/reveryday.github.io.git
  branch: main
```

安装deploy-git （部署的命令）：

```bash
$ npm install hexo-deployer-git --save
```

安装完成后：

```bash
$ hexo clean
$ hexo g
$ hexo d
```

其图片显示的默认路径为："D:\Program Files\HexoBlog\Blog\source"。

### 2-Butterfly主题配置

Butterfly主题项目地址：https://github.com/jerryc127/hexo-theme-butterfly

#### 1-代码高亮

相关配置在根目录下的_config.yml中：

<img src="https://gitee.com/wenswuu/pictures/raw/master/20250402154329935.webp" style="zoom:67%;" />

代码高亮需要先选择code language，然后网页端就也高亮显示了：

![](https://gitee.com/wenswuu/pictures/raw/master/20250402154325913.webp)

具体配色在 themes\butterfly\source\css\_highlight\theme.styl 中，我highlight theme选择的是light，参考jupyter notebook的配色改了一下：

<img src="https://gitee.com/wenswuu/pictures/raw/master/20250402154333412.webp" style="zoom:67%;" />

#### 2-latex配置

引入数学公式库只要在themes/butterfly/_config.yml中打开math的配置就行：

<img src="https://gitee.com/wenswuu/pictures/raw/master/20250402154339635.webp" style="zoom:67%;" />

#### 3-图床

Markdown很大的一个弊端在于，如果需要插入图片，一般选择相对的路径（如./Imgaes.p1.png)，这样管理图片就很麻烦，比如图片的命名、存储等等，得益于网友的建设，可以结合gitee配置图床（使用Piclist、Picgo等），完美解决这个问题。

#### 4-About页面

首先在https://www.iconfont.cn/注册一个账号，然后找到对应的图标，在主题配置文件config.yaml中导入：

```yaml
inject:
  head:
    - <link rel="stylesheet" href="https://at.alicdn.com/t/c/font_5073185_9ng9btivjo.css">
```

在source/about/index.md中：

```html
<a href="https://blog.csdn.net/wensww?spm=1000.2115.3001.5343" target="_blank" style="margin-right: 20px; text-decoration: none;">
  <span class="iconfont icon-csdn" style="color: #FC5531;"></span> 我的 CSDN
</a>
```

### 3-遇到的问题

1-安装时显示无法连接：

```cmd
PS D:\Program Files\HexoBlog\blog> git clone -b master https://github.com/jerryc127/hexo-theme-butterfly.git themes/butterfly
Cloning into 'themes/butterfly'...
fatal: unable to access 'https://github.com/jerryc127/hexo-theme-butterfly.git/': Failed to connect to github.com port 443 after 21127 ms: Could not connect to server
```

chrome打开[https://github.com](https://github.com/) 是没啥问题的，试了很多次都是无法连接，可直接去GitHub上手动下载。

2-bash: hexo: command not found（突然无法找到hexo指令）

```bash
$ hexo clean
bash: hexo: command not found
```

尝试了重新全局安装hexo也没用：

```bash
$ npm install -g hexo-cli

changed 53 packages in 7s

14 packages are looking for funding
  run `npm fund` for details

$ hexo clean
bash: hexo: command not found
```

原因是环境变量未更新，在安装全局 npm 包时，npm 的全局包路径需要添加到系统的 PATH 环境变量中，只需添加 npm 全局包路径重启终端即可，其通常为：

```
C:\Users\用户名\AppData\Roaming\npm
```

