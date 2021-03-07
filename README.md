# 课表日历订阅

## 使用方式

1. （PC端）进入大连理工大学教务处，进入新的选课系统，查看课表

2. 按下F12，进入开发人员调试模式

3. 切换显示未大课表格式

4. 在调试工具的Network选项下，复制如下内容：

   ![image-20210307201142268](https://frozenwhale.oss-cn-beijing.aliyuncs.com/img/image-20210307201142268.png)

5. 将上述内容复制到文本文件`data.json`中（可以通过先创建`.txt`然后修改文件后缀实现）

6. 将`data.json`添加到如下目录，层次应如下所示：

   ```
    ── dlut_timetable
       ├── README.md
       ├── data.json
       ├── main.py
       └── timetable.ics(optional)
   ```

7. 在`dlut_timetable`目录下运行`main.py`，得到`timetable.ics`，即可导入手机日历/电脑日历

## 预览

![image-20210307202059624](https://frozenwhale.oss-cn-beijing.aliyuncs.com/img/image-20210307202059624.png)

## 局限

- 由于本人为外校学生，因此对于dlut的教务以及统一认证不是很熟悉，尝试自动订阅但是发现课表url未登录会被以前的登录界面拦截，因此目前局限于手动导入课表json数据

  