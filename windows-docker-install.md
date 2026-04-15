# Windows Docker 安装教程

## 环境要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10 64位（版本 2004+）或 Windows 11 |
| 功能 | WSL 2 已启用 |
| 硬件 | 开启 BIOS 虚拟化（VT-x / AMD-V） |
| 内存 | 建议 ≥ 8GB |

---

## 一、启用 WSL 2

以**管理员身份**打开 PowerShell，依次执行：

```powershell
# 启用 WSL
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# 启用虚拟机平台
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

重启电脑后，继续执行：

```powershell
# 设置 WSL 默认版本为 2
wsl --set-default-version 2
```

> 如提示需要更新内核，访问：https://aka.ms/wsl2kernel 下载安装后再继续。

---

## 二、安装 Docker Desktop

1. 访问官网下载安装包：https://www.docker.com/products/docker-desktop/
2. 运行 `Docker Desktop Installer.exe`
3. 安装选项中确认勾选 **Use WSL 2 instead of Hyper-V**
4. 完成安装后重启电脑

---

## 三、国内镜像加速配置（推荐）

打开 Docker Desktop → Settings → Docker Engine，在 JSON 中添加：

```json
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://dockerproxy.com",
    "https://mirror.baidubce.com"
  ]
}
```

点击 **Apply & Restart**。

---

## 四、验证安装

打开 PowerShell 或 CMD：

```bash
# 查看版本
docker --version

# 运行测试容器
docker run hello-world
```

看到 `Hello from Docker!` 输出即表示安装成功。

---

## 五、常用命令速查

```bash
# 查看运行中的容器
docker ps

# 查看所有容器
docker ps -a

# 拉取镜像
docker pull nginx

# 启动容器
docker run -d -p 8080:80 nginx

# 停止容器
docker stop <容器ID>

# 删除容器
docker rm <容器ID>

# 查看镜像列表
docker images
```

---

## 六、常见问题

**Q: 提示 WSL 2 installation is incomplete？**  
A: 下载并安装 WSL2 内核更新包：https://aka.ms/wsl2kernel

**Q: Docker Desktop 启动后一直转圈？**  
A: 以管理员身份运行，或检查 Hyper-V / 虚拟化是否在 BIOS 中开启。

**Q: 拉取镜像超时？**  
A: 配置镜像加速（见第三步），或使用代理。

**Q: WSL 内存占用过高？**  
A: 在 `%UserProfile%\.wslconfig` 中限制内存：

```ini
[wsl2]
memory=4GB
processors=2
```
