---
name: pay-nsq-send
description: 金融云环境 NSQ 消息发送工具。用于向指定 topic 发送 NSQ 消息，支持 SC 环境。当用户需要发送 NSQ 消息、测试 NSQ 消费方、调试消息队列时使用。
tags: devops, general
author: wangxijie
created: 2026-03-09
updated: 2026-03-09T19:00:00.000Z
---
# NSQ Send - NSQ 消息发送

## 使用方式

```bash
python3 $SKILL_DIR/scripts/nsq_send.py \
  --topic <NSQ Topic> \
  --msg '<消息体JSON>' \
  [--sc <SC环境标识>] \
  [--address <NSQ地址>] \
  [--port <端口>]
```

## 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--topic` | 是 | NSQ 消息 Topic |
| `--sc` | 否 | SC 持续集成环境标识（如 `prj0089187`），可为空 |
| `--msg` | 是 | 消息体，JSON 字符串 |
| `--address` | 否 | NSQ 地址，默认 `finbj2-qa-nsq6` |
| `--port` | 否 | NSQ 端口，默认 `4151` |

## 调用原理

通过 NSQ HTTP API 直接发送消息：
- 无 SC 时调用 `POST /pub?topic=<topic>`
- 有 SC 时调用 `POST /pub_ext?topic=<topic>&ext=<url_encoded_dispatch_tag>`，ext 中包含 `{"##client_dispatch_tag":"<sc>"}`

## 示例

### 基本用法（无 SC）

```bash
python3 $SKILL_DIR/scripts/nsq_send.py \
  --topic trade_order_changed \
  --msg '{"orderId":"E20260309000001","status":"PAID"}'
```

### 指定 SC 环境

```bash
python3 $SKILL_DIR/scripts/nsq_send.py \
  --topic trade_order_changed \
  --sc prj0089187 \
  --msg '{"orderId":"E20260309000001","status":"PAID"}'
```

### 指定 NSQ 地址和端口

```bash
python3 $SKILL_DIR/scripts/nsq_send.py \
  --topic trade_order_changed \
  --msg '{"orderId":"E20260309000001","status":"PAID"}' \
  --address finbj2-qa-nsq6 \
  --port 4151
```
