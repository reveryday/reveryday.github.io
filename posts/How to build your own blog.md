---
title: How to build your own blog
date: 2025-02-09 21:53:10
tags: Tool
---

### Hexo

1. 安装Git，安装好后检查版本信息；

2. 安装nodejs：Hexo是基于nodejs编写的，需安装nodejs和里面的npm工具， npm会随Node.js一起安装。安装好后需将npm的全局包路径需要添加到系统的 PATH 环境变量中，并检查版本信息；

3. 安装hexo，全局安装：

   ```
   $ npm install -g hexo-cli
   ```

   初始化：

   ```
   $ hexo init Blog
   $ npm install
   
   up to date in 1s
   
   24 packages are looking for funding
     run `npm fund` for details
   $ ls
   _config.landscape.yml  db.json    node_modules/      package.json  scaffolds/  themes/
   _config.yml            deploy.sh  package-lock.json  public/       source/
   ```

4. 生成SSH添加到GitHub：配置 Git 的全局用户名和邮箱。

   ```
   $ git config --global user.name"you_github_user_name"
   $ git config --global user.email"your_github_email"
   ```

   检查是否配置成功：

   ```
   $ git config --global --list
   user.name=you_github_user_name
   user.email=your_github_email
   core.autocrlf=true
   ```

   创建SSH密钥：

   ```
   $ ssh-keygen -t rsa -C "your_github_email"
   ```

   在GitHub-setting中，找到SSH keys的设置选项，点击New SSH key，把 C:\Users\34001\.ssh\id_rsa.pub 里内容复制进去，查看是否成功：

   ```
   $ ssh -T git@github.com
   Hi reveryday! You've successfully authenticated, but GitHub does not provide shell access.
   ```

5. 将hexo部署到GitHub：打开站点配置文件  _config.yml ，翻到最后，修改为：

   ```
   deploy:
     type: git
     repo: https://github.com/reveryday/reveryday.github.io.git
     branch: main
   ```

   安装deploy-git：

   ```
   $ npm install hexo-deployer-git --save
   ```

   则配置完成！
