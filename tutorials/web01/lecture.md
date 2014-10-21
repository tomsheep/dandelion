# Web 01 - Environment Setup

## 连接开发服务器
开发环境是做事的开始，不要忽视这个步骤。推荐使用`*nix系统`作为开发环境，虽然Windows是一个伟大的操作系统，但它对开发者来说并不十分便利。如果你已经在使用Linux或Mac OS X，那么太好了，这个步骤就变得异常容易；如果不是，那么你需要阅读下面的教程。

为了方便，我提供了一个远程机器作为开发机，小蒲可以在上面完成学习，而不用自己准备环境。昨天给出的`tomsheep.net`主机在纽约，连接稍显迟钝，所以我准备了另一台在新加坡的机器，使用起来就轻快很多。地址是`dev.tomsheep.net`，用户名是pys，密码和昨天的一样。

### Linux/Mac OS X
打开term, 直接输入

    ssh pys@dev.tomsheep.net

### Windows
Windows系统没有自带ssh客户端，一般大家会用自己喜欢的termial，比如putty, securecrt等。这里我推荐使用securecrt，软件可以在底部的工具链接里找到，配置方法在[securecrt.md](securecrt.md)中详细介绍。


## 熟悉Git
Git是目前最为流行的版本控制工具，和CVS或SVN不同，他是一个`分布式`的系统，每个人在本地check out出的是一个完整的repository，包含所有历史版本，而非一个当前最新版本的snapshot(如SVN)。理解Git，`链表`是它的核心
+ 一个Git仓库可以包含若干`branch`, 比如, 创建之初会有默认的`master` branch，每个branch由一系列的`commit`组成，一个branch通过将自己的`HEAD`指向某个commit而实现分支管理
+ 注意`工作区`（你本地的目录）、`暂存区`（提交到当前分支之前的一个备选状态，为什么有这样一个概念先不去理会）以及`版本库`的概念
+ 通常地，一个commit从创建到提交经过了如下步骤
    + 修改文件
    + git status 查看修改状态
    + git add <修改/或添加的文件>  # 将修改的内容加入暂存区
    + git commit -m "修改说明"   # 提交commit，把暂存区的所有内容提交到当前分支，此时只是提交到了本地，并没有上传到远程公共库
    + git push `<origin名>` `<branch名>`  # 常见的 `git push origin master`的意思就是说把本地当下的branch提交到origin这个库的master分支
    + 上面这个push实际上隐含了一个merge的过程，如果你的修改可以自动merge到目标分支，则会成功返回。如果发生冲突，你需要现在本地完成merge，然后再提交
    + git pull `<origin>` `<branch>`   # 把远程origin库的branch分支拉回到本地，并和本地当前分支进行合并，相当于 git fetch + git merge
+ 由于多人协作时让冲突更容易处理，很多团队都会推行所谓`GitHub Flow`，以github作为仓库软件，当一个队员要进行某个feature开发时
    + 所有人不应该对master分支进行直接修改
    + git checkout -b feature1   # 将当前本地branch切换到feature1，如果没有这个分支，则以之前branch的头为起点，创建feature1这个新branch
    + 进行修改，完成这个功能
    + git add . -A  # 添加所有修改到暂存区
    + git commit -m "blahblah"  # 提交到当前分支，也就是feature1
    + git checkout master  # 切换到master分支
    + git pull origin master  # 因为这段时间内master分支可能有了新的内容进入，所以这里的目的是确保本地master是最新的
    + git merge feature1  # 把feature1的修改merge到当前分支（也就是master），这里可能出现冲突，则需要进行手动merge确保merge后的代码可用
    + git push origin feature1  # 把当前分支（master）提交到origin库的feature1分支, 其实就是新建这个分支
    + 为什么不直接push到master分支呢？其实也是可以的，但不推荐这样的协作流程
    + 然后到github项目上`create a pull request`, 选择从源feature1，目标master分支
    + 这个pull request经过同伴的review通过后，github上点击merge，你的修改这时才进入了master分支

## 延伸阅读
+ [简易Git教程](http://www.liaoxuefeng.com/wiki/0013739516305929606dd18361248578c67b8067c8c017b000)

## 工具下载
+ [百度云盘链接](http://pan.baidu.com/s/1ntNuak5)
+ 密码: udgu


## Homework
0. 成功连接dev.tomsheep.net, 获取它的公网IP
1. 什么是SSH？
2. Git和GitHub是什么关系？
3. 上面描述的GitHub Flow有什么好处？
4. 把上面几个问题的答案写到外面submit文件夹中，然后按照上述GitHub Flow，提交一个pull request给我

