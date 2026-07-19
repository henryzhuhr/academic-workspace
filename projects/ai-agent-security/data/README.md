# Data Register

项目默认数据分类见 `../project.json`。开始收集或导入任何数据前，阅读 [工作区数据管理规范](../../../methods/data-management.md)。

当前阶段没有项目数据集。研究材料来自公开文献、标准和安全框架；引用元数据进入 `literature/bibliography.bib`，全文仅通过 `literature/files` 外部入口访问。

| Dataset ID | Description | Source and acquired | License / ethics | Classification | Storage location | Version / checksum | Processing |
| --- | --- | --- | --- | --- | --- | --- | --- |
| _None_ | No project dataset in the literature-review phase | — | — | `internal` | — | — | — |

使用逻辑数据集标识、仓库相对入口或可移植 URI 作为登记位置。设备专属绝对路径可写入被 Git 忽略的 `locations.local.json`，但不得成为唯一定位信息。

## Access and retention

- Authorized users: repository collaborators
- Backup strategy: Git for notes and metadata; external library policy for literature files
- Retention or deletion requirement: follow source licences and workspace literature policy
- Contact or data steward: project owner

不得在本文件中记录密码、访问令牌、私钥或个人身份信息。
