1. GET请求通过URL传参，很容易被修改，攻击者可以通过修改URL参数轻易地修改数据值，甚至进行攻击。
   假设修改用户收入的请求通过GET实现，如

       http://example.com/update?id=21&income=1000

    该请求会使后台执行一条数据库update语句，从而使id为21的用户的收入变为1000。但攻击者可以很方便将income参数的值改变，从而篡改了用户实际的收入。攻击者甚至可以利用提交的参数进行其他更严重的攻击，如SQL注入等。

2. 项目在windows下直接运行会报错，好像没法从web文件中读取地址直接引入webpy库，所以我加了sys.path先跑起来。net.py那边也有个报错，Google了下暂时改了。
blog示例代码已读，依葫芦画瓢是没问题，但是因为codeacademy上的Python课程有错误没法加载，所以Python还没看。以前用Python写过点数据处理的小脚本，但看webpy代码的时候，还是觉得很多语法和规则比较陌生，所以还要再重新学下Python。

3. 平时工作也用的是Chrome Dev Tools，Fiddler有装但基本没用过。。。
