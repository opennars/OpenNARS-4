# PyNARS

#### 介绍
Python implementation of NARS (Non-Axiomatic-Reasoning-System).

Reference:
 - OpenNARS 3.0.4, 
 - The Design Report of OpenNARS 3.1.0


#### 运行环境

 - Python版本: 3.7.10. 
     - 只有这个版本被测试过，但Python 3.7以及更高的版本应该都可以接受。
 - 操作系统: Windows 10. 
     - 仅在这个操作系统下做过测试，但其他的操作系统或许也可以。
 - 依赖包: 见`requirements.txt`.
     - 请注意包`tqdm` 的版本不应超过3.1.4，否则颜色显示可能会异常。这是因为高版本`tqdm`中的BUG会导致包`sty`和`tqdm`之间的冲突，`sty`的颜色显示会出现错误。然而，这一约束不是必须的，即如果你不介意颜色显示异常则高版本的`tqdm`也可接受。异常显示只有在第一次运行PyNARS过程中构建稀疏查找表(SparseLUT)时出现。

#### 安装教程


    pip install pynars


#### 使用说明

1.  复制文件`pynars/config.json`到你的工作目录。 *(可选)*
2.  在工作目录下，运行命令`python -m pynars.Console`。若需要运行`*.nal`文件，则运行命令`python -m pynars.Console <文件名.nal>`。
3.  在控制台中输入纳思语(Narsese)，输入正整数运行一定的推理周期，或输入`'`开头的字符串作为i注释（例如`' 这是一条注释`）。
4.  按下`ctrl`+`C`退出。

#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request
