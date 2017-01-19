# Blog

个人博客，使用 [Hugo](https://gohugo.io) 创建。

博客发布用了个 Python 写的 WEB 服务器，见 autobuild 分支。利用 coding.net 的 webhook 在代码仓库有更新后立即构建并上传到腾讯云对象存储上。 

自动部署服务使用了 daocloud.io 自动构建 Docker 镜像并部署到腾讯云主机上。
