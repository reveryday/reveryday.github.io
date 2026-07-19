# 访客统计部署说明（IP 属地 + 设备）

博客每个页面已内置一段统计脚本。访客打开页面时，会收集：

- **IP 属地**：国家 / 省份 / 城市 / 运营商（像微博「IP 属地：四川」那样，精确到省市）
- **设备**：电脑 or 手机、操作系统、浏览器、屏幕分辨率、浏览器语言
- **来源**：访问的页面、从哪个网站跳转来的、时间

这些数据**只写入你私有的 Google 表格**，接口只写不读，访客无法看到任何历史记录。

> ⚠️ 隐私提醒：IP 属于个人信息。自用没问题，但**不要把访客 IP / 属地公开展示在博客上**。

---

## 一、创建 Google 表格 + 接口（在你自己的 Google 账号里操作，约 5 分钟）

1. 打开 <https://sheets.google.com>，新建一个空白表格，命名如「博客访客」。
2. 顶部菜单 **扩展程序 → Apps Script**，会打开代码编辑器。
3. 删掉里面自带的 `function myFunction() {}`，把下面「二、Apps Script 代码」整段粘进去，保存（💾）。
4. 右上角点 **部署 → 新建部署**。
5. 点齿轮选择类型 **Web 应用（Web app）**，然后：
   - **执行身份 / Execute as**：选 **我（Me）**
   - **谁可以访问 / Who has access**：选 **任何人（Anyone）**
     （必须选这个，匿名访客才能把记录写进来；但表格本身仍是私有的，别人看不到）
6. 点 **部署**，首次会要求授权 → 用你的账号授权（若提示「未验证」，点「高级 → 继续」即可，这是你自己的脚本）。
7. 复制出现的 **Web 应用网址**（形如 `https://script.google.com/macros/s/AKfyc.../exec`）。

---

## 二、Apps Script 代码

```javascript
function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName('visits') || ss.insertSheet('visits');
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(['时间', 'IP', '国家', '省份', '城市', '运营商',
        '设备', '浏览器', '系统', '屏幕', '语言', '页面', '来源', 'UserAgent']);
    }
    var d = JSON.parse(e.postData.contents);
    sheet.appendRow([
      new Date(), d.ip || '', d.country || '', d.region || '', d.city || '',
      d.isp || '', d.device || '', d.browser || '', d.os || '', d.screen || '',
      d.language || '', d.page || '', d.referrer || '', d.ua || ''
    ]);
    return ContentService
      .createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}
```

---

## 三、把网址填进博客

1. 打开 `blog_builder/config.py`，找到 `var ENDPOINT = "";`（在 `FOOTER_SCRIPTS` 里的访客统计段落）。
2. 把第一步复制的 Web 应用网址粘进去：
   ```javascript
   var ENDPOINT = "https://script.google.com/macros/s/AKfyc.../exec";
   ```
3. 重新构建并部署：
   ```bash
   python build.py
   git add -A && git commit -m "启用访客统计" && git push
   ```
   推送后 GitHub Actions 会自动发布。

---

## 四、查看数据

回到那张 Google 表格，会自动出现一个 **visits** 工作表，每来一个访客就多一行，包含 IP 属地、省份、设备等。你可以在表格里排序、筛选（比如筛出「四川」）、导出。

---

## 说明与局限

- **属地精度**：靠 IP 库反查，精确到省 / 市，拿不到街道。用 VPN / 代理 / 部分移动网络时会不准 —— 微博也一样。
- **IP 来源**：用免费服务 `ipwho.is` 查询（HTTPS、无需密钥）。若哪天它不可用，可换成 `https://ipapi.co/json/`（字段名相近，`region` 即省份）。
- **去重**：同一标签页会话内、同一页面只记一次，避免刷新刷屏；换页面或重开标签页会记新的一条。
- **失败兜底**：若 IP 查询失败，仍会上报设备信息，只是属地为空。
