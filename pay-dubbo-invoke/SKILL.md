---
name: pay-dubbo-invoke
description: |
Dubbo 接口调用工具。用于验证 Dubbo 服务接口行为，支持 QA/SC 环境联调与功能测试。
触发场景：用户需要调用 Dubbo 接口做功能验证、联调排障、回归检查。
执行方式：QA 环境可直接调用；Pre/Prod 环境生成 curl tether 命令并在容器或跳板机执行。
---

# Dubbo Invoke - Dubbo 接口调用

## 使用方式

```bash
bash $SKILL_DIR/scripts/dubbo_invoke.sh \
  --interface <接口全限定名> \
  --method <方法名> \
  --data '<JSON 数组入参>' \
  [--env qa|pre|prod] \
  [--sc <SC环境标识>]
```

## 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--interface` | 是 | Dubbo 接口全限定名 |
| `--method` | 是 | 方法名 |
| `--data` | 是 | **JSON 数组**，每个元素对应一个方法入参（按顺序） |
| `--env` | 否 | 环境：`qa`（默认，直接调用）、`pre`/`prod`（生成 curl 命令） |
| `--sc` | 否 | SC 持续集成环境标识（如 `prj0089187`），不传则访问基础 QA |

## 环境说明

| 环境 | 行为 | 网关 |
|------|------|------|
| `qa` | **直接执行**调用 | `tether-qa.s.qima-inc.com` |
| `pre` | 仅**生成 curl 命令**（支持 SC） | `tether-pre.s.qima-inc.com` |
| `prod` | 仅**生成 curl 命令** | `tether.s.qima-inc.com` |

> Pre/Prod 因网络隔离无法本地调用，需将生成的 curl 命令复制到对应环境的容器或跳板机上执行。

## 示例

### QA 环境直接调用（默认）

```bash
bash $SKILL_DIR/scripts/dubbo_invoke.sh \
  --interface com.youzan.pay.customercore.common.api.configinfo.PayConfigQueryService \
  --method queryChannelPayConfig \
  --data '[{"userNo":"210429164050000000","type":3}]''
```

### SC 环境调用

```bash
bash $SKILL_DIR/scripts/dubbo_invoke.sh \
  --interface com.youzan.pay.customercore.common.api.configinfo.PayConfigQueryService \
  --method queryChannelPayConfig \
  --sc prj0087551 \
  --data '[{"userNo":"210429164050000000","type":3}]''
```

### Pre 环境生成 curl 命令

```bash
bash $SKILL_DIR/scripts/dubbo_invoke.sh \
  --env pre \
  --interface com.youzan.pay.customercore.common.api.configinfo.PayConfigQueryService \
  --method queryChannelPayConfig \
  --data '[{"userNo":"210429164050000000","type":3}]'
```
