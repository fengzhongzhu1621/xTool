# 国际化（Internationalization，i18n）
当页面被移植到不同的语言及地区时，页面本身不用做改变或修正。

# 本地化（localization，l10n）
为特定区域翻译文件，并为了使页面能在该特定语言环境或地区使用，而应用特殊布局、加入本地特殊化组件等的过程。
国际化只需做一次，但本地化则要针对不同的区域各做一次。


# ISO Language Code Table
http://www.lingoes.net/en/translator/langcode.htm

# 设置页面的主语言

对于多语言网站，应为每种语言的页面重置主语言，
```html
<html lang="en">
```

# 设置 hreflang 属性

## a 标签
多语言网站里通常包含指向其他语言版本的网站链接，可以使用 hreflang 属性用于指定被链接文档的语言。
hreflang 属性的值也是 ISO 标准的双字符语言代码。
hreflang 属性不会指定标签中的内容所使用的语言，而是指定被 href 属性调用的文档所使用的语言。

```html
<a href="https://xxx.xx.xx" hreflang="zh">zh</a>
```

## link 标签

设置搜索引擎显示的指定语言的链接。

```angular2html
<link rel="alternate" hreflang="en-us" href="https://websitename.com/en-us" />
<link rel="alternate" hreflang="x-default" href="https://www.websitename.com" />
```

# 字符编码

```angular2html
<meta charset="UTF-8">
```

# 自动检测语言

检测方法
* IP 地址
* HTTP请求的头部信息 Accept-Language
* 浏览器语言 navigator.languages

# 语言存储
用于用户切换语言后保存当前设置。

* cookie
* local storage
* service worker
