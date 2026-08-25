---
id: web-change-monitor
name: web-change-monitor
description: 网页变更主动监控与语义提醒插件。为 Agent 提供后台持续监听、文本 Hash 过滤与 LLM 语义识别评估的工具集。
version: 1.0.0
---

# Web Change Monitor Plugin Specification

## 1. 核心定位 (Purpose)
本插件专为 AgentScope / QwenPaw 架构设计，解决 LLM 无法“跨时间线主动监听网页变化”的核心短板。通过将抓取与比对封装为标准 Tool 功能，支持 Agent 随时注册监控任务与调起主动检查。

## 2. 工具列表 (Provided Tools)
- `add_monitor_task`: 注册新网页监控规则。
- `run_monitor_check`: 执行抓取与 AI 语义评估。
