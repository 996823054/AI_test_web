export const navGroups = [
  {
    label: '质量工作台',
    items: [
      {
        to: '/overview',
        label: '首页 / 质量驾驶舱',
        desc: '健康状态、资产概览与快捷入口',
      },
    ],
  },
  {
    label: '测试资产中台',
    items: [
      {
        to: '/requirements',
        label: '需求中心',
        desc: '需求文档库、原文预览与入库门禁',
      },
      {
        to: '/cases',
        label: 'Case 中心',
        desc: '正式 case 资产、来源追溯与覆盖信息',
      },
      {
        to: '/apis',
        label: '接口中心',
        desc: '接口事实源、环境变量与调试入口',
      },
    ],
  },
  {
    label: '执行与证据',
    items: [
      {
        to: '/executions',
        label: '执行中心',
        desc: '任务、日志、取消与重试',
      },
      {
        to: '/reports',
        label: '报告中心',
        desc: '报告、证据与导出',
      },
      {
        to: '/mobile',
        label: '移动端执行中心',
        desc: '设备、App 与移动端执行',
      },
    ],
  },
  {
    label: '智能与治理',
    items: [
      {
        to: '/ai',
        label: 'AI 能力中心',
        desc: 'Skill / Prompt / Evaluator',
      },
      {
        to: '/changes',
        label: '变更中心',
        desc: 'ChangeRecord 与影响分析',
      },
      {
        to: '/todos',
        label: '待办中心',
        desc: '待办注册与核销闭环',
      },
    ],
  },
  {
    label: '系统设置',
    items: [
      {
        to: '/settings',
        label: '系统设置',
        desc: 'AI 模型、脱敏规则与报告策略',
      },
    ],
  },
]

export const hiddenUntilImplemented = []
