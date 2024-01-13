"""
FEEL (Friendly Enough Expression Language) 语法解析器，用于对 FEEL 语法表达式进行解析和运算，得到对应的 Python 对象作为计算结果。
FEEL 是 OMG (Object Management Group) 定义的 DMN (Decision Model and Notation) 规范中的一部分。可用于决策引擎 (DMN) 中决策表达式的解析。

DMN (Decision Model and Notation)
DMN应该被认为是一种适用于任何类型的商业逻辑的低代码语言，而不仅仅是我们通常认为的商业决策逻辑。
DMN 是一种用于精确规范业务决策和业务规则的建模语言和符号。参与决策管理的不同类型的人都可以轻松阅读 DMN。
DMN 旨在与 BPMN 和/或 CMMN 一起工作，提供一种机制来对与流程和案例相关的决策进行建模。
虽然 BPMN、CMMN 和 DMN 可以独立使用，但它们经过精心设计以相互补充。BPMN、CMMN和DMN真正构成了流程改进标准的“三冠王”。
决策模型和表示法（DMN）是对象管理小组（OMG）建立的用于描述和建模操作决策的标准。
DMN定义了一个XML模式，该模式使DMN兼容平台之间以及整个组织之间可以共享DMN模型，以便业务分析人员和业务规则开发人员可以在设计和实现DMN决策服务时进行协作。DMN标准类似于并可以与业务流程模型和表示法（BPMN）标准一起使用，以设计和建模业务流程。

FEEL 中的规则表达式
https://access.redhat.com/documentation/zh-cn/red_hat_decision_manager/7.13/html/developing_decision_services_in_red_hat_decision_manager/dmn-feel-con_dmn-models

表达式语言 2.0
Expression Language 2.0(简称 DMN SFEEL)，它是足够友好的表达语言 (FEEL) 的子集，为规则条件提供标准语法，并在建模规则时减少歧义。
https://help.sap.com/docs/business-rules/business-rules-capability-for-neo-environment/expression-language-2-0?locale=zh-CN

FEEL语法详解 - Part I
http://www.willking.tech/feel-grammar-detail-part-1/
http://www.willking.tech/feel-grammar-detail-part-2/
http://www.willking.tech/feel-grammar-detail-part-3/
http://www.willking.tech/feel-grammar-detail-part-4/
http://www.willking.tech/feel-grammar-detail-part-5/
"""
