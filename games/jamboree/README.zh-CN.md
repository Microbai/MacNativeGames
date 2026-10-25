# 超级马里奥派对 空前盛会：实验性 Mac 原生移植

[English](README.md) · [渲染修复原理](docs/rendering-fix.md) · [验证记录](docs/validation.md) · [来源](third_party/COPIES.md) · [许可证](THIRD_PARTY_NOTICES.md)

仅验证 **2.3.0 / v458752**，标题 ID `0100965017338000`。已测试开场、角色选择和广场，属于早期移植；尚未验证全部棋盘、小游戏、体感和多人玩法。

游戏 ARM64 指令经过离线改写后在苹果芯片上原生执行，宿主负责必要的系统服务，NVN 图形调用转换为 Metal。没有 CPU 解释器、CPU JIT 或动态 CPU 翻译。Metal 在运行时编译 GPU 着色器，与 CPU 原生执行是不同环节。

本次修复让“关闭光栅化、未启用变换反馈”的顶点着色器仍能写入角色变形数据，解决未初始化顶点导致的大三角形拉伸。没有隐藏三角形、跳过角色网格或改变角色状态。

## 构建方法

需要支持 Metal 4 的苹果芯片 Mac、macOS 26+、Xcode/macOS 26+ SDK、Python 3.11+、.NET SDK 10、`make`、`clang`、`zstd`、`spirv-cross`。Python 依赖为 `lz4 capstone fonttools`，3.14 以前另需 `backports.zstd`。首次恢复 .NET 提取工具依赖需要联网。当前只提供 Mac 构建入口，iOS 未编译、未测试。

自行提供未经修改的本体 NSP/XCI、**2.3.0 更新 NSP** 和 `prod.keys`。本体和更新放在同一文件夹；无可识别票据时，文件名应含 `[标题ID]`，更新文件另含 `[v458752]`。提取后还会核对三个 NSO 的完整 SHA-256、大小和 build ID，文件名不能绕过校验。其他版本、DLC 和压缩容器不在支持范围内。

在仓库根目录执行：

```sh
python3 games/jamboree/scripts/build_jamboree.py \
  /你的游戏输入文件夹 \
  --keys /你的密钥位置/prod.keys \
  --work-dir /私人构建目录/Jamboree-build \
  --output '/私人产出目录/Super Mario Party Jamboree.app' \
  --language zh-Hans
```

构建与产出目录放在 Git 仓库外，至少预留 **25 GB** 可用空间。构建器把所需源码与工具复制到工作目录，从原始游戏输入生成结果；重复构建按指纹复用阶段。输出 App 已存在时会拒绝覆盖，请选择新路径或自行移走旧版本。不要手改改写后的二进制。

首次着色器准备需要数分钟。App 使用本机临时签名并验证，不做公证；运行不依赖 Python 或 .NET。仓库不包含游戏文件、游戏着色器、密钥或存档。

## 使用与存档

双击生成的 App 启动。WASD 是左摇杆，方向键是十字键，J/K/U/I 对应 A/B/X/Y，Q/E/Z/C 对应 L/R/ZL/ZR，Return/Tab 对应加号/减号，F/G 对应摇杆按下。

Mac 菜单可选择手柄布局、交换 A/B 和全屏，选择会保存。自动模式依据手柄名称识别 Nintendo 布局；通用名称的手柄可以手动选择。此次验证包含配置读取与保存，没有实际按压物理手柄、测试体感或多人同时输入。

存档位于 `~/Library/Application Support/Super Mario Party Jamboree/save/`，同级包含临时文件、`controller-layout.txt` 和 `last-launch.log`。重新打包不覆盖存档。测试新运行时前建议备份存档；不要把这些文件加入提交。

目前部分场景首次遇到着色器时会有约 9–17 秒停顿或短暂白屏，之后恢复渲染。完整着色器构建仍有 3 项既有 subgroup 翻译失败，具体范围见[验证记录](docs/validation.md)。局部场景约 60 FPS 不代表完整游戏稳定可玩。

## 验证命令

```sh
python3 -m unittest discover -s tests
make -C games/jamboree test
make -C games/jamboree test-gpu WORK=/私人构建目录/Jamboree-gpu-tests
```

目录内包含独立运行时、图形层、离线改写器、预编译着色器翻译工具、构建脚本、输入版本校验、回归测试和第三方许可。不会调用其他游戏目录。完整依赖说明、目录清单和构建记录见英文 README 与来源文档。
