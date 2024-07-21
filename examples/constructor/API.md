# API Reference <a name="API Reference" id="api-reference"></a>

## Constructs <a name="Constructs" id="Constructs"></a>

### AIAgent <a name="AIAgent" id="@yike5460/intelli-agent.AIAgent"></a>

#### Initializers <a name="Initializers" id="@yike5460/intelli-agent.AIAgent.Initializer"></a>

```typescript
import { AIAgent } from '@yike5460/intelli-agent'

new AIAgent(scope: Construct, id: string, props: AIAgentProps)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#@yike5460/intelli-agent.AIAgent.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | *No description.* |
| <code><a href="#@yike5460/intelli-agent.AIAgent.Initializer.parameter.id">id</a></code> | <code>string</code> | *No description.* |
| <code><a href="#@yike5460/intelli-agent.AIAgent.Initializer.parameter.props">props</a></code> | <code><a href="#@yike5460/intelli-agent.AIAgentProps">AIAgentProps</a></code> | *No description.* |

---

##### `scope`<sup>Required</sup> <a name="scope" id="@yike5460/intelli-agent.AIAgent.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

---

##### `id`<sup>Required</sup> <a name="id" id="@yike5460/intelli-agent.AIAgent.Initializer.parameter.id"></a>

- *Type:* string

---

##### `props`<sup>Required</sup> <a name="props" id="@yike5460/intelli-agent.AIAgent.Initializer.parameter.props"></a>

- *Type:* <a href="#@yike5460/intelli-agent.AIAgentProps">AIAgentProps</a>

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#@yike5460/intelli-agent.AIAgent.toString">toString</a></code> | Returns a string representation of this construct. |

---

##### `toString` <a name="toString" id="@yike5460/intelli-agent.AIAgent.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#@yike5460/intelli-agent.AIAgent.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |

---

##### ~~`isConstruct`~~ <a name="isConstruct" id="@yike5460/intelli-agent.AIAgent.isConstruct"></a>

```typescript
import { AIAgent } from '@yike5460/intelli-agent'

AIAgent.isConstruct(x: any)
```

Checks if `x` is a construct.

###### `x`<sup>Required</sup> <a name="x" id="@yike5460/intelli-agent.AIAgent.isConstruct.parameter.x"></a>

- *Type:* any

Any object.

---

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#@yike5460/intelli-agent.AIAgent.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |
| <code><a href="#@yike5460/intelli-agent.AIAgent.property.api">api</a></code> | <code>aws-cdk-lib.aws_apigateway.RestApi</code> | The API Gateway for the AI agent. |
| <code><a href="#@yike5460/intelli-agent.AIAgent.property.lambdaFunction">lambdaFunction</a></code> | <code>aws-cdk-lib.aws_lambda.Function</code> | The Lambda function for the AI agent. |

---

##### `node`<sup>Required</sup> <a name="node" id="@yike5460/intelli-agent.AIAgent.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `api`<sup>Required</sup> <a name="api" id="@yike5460/intelli-agent.AIAgent.property.api"></a>

```typescript
public readonly api: RestApi;
```

- *Type:* aws-cdk-lib.aws_apigateway.RestApi

The API Gateway for the AI agent.

---

##### `lambdaFunction`<sup>Required</sup> <a name="lambdaFunction" id="@yike5460/intelli-agent.AIAgent.property.lambdaFunction"></a>

```typescript
public readonly lambdaFunction: Function;
```

- *Type:* aws-cdk-lib.aws_lambda.Function

The Lambda function for the AI agent.

---


## Structs <a name="Structs" id="Structs"></a>

### AIAgentProps <a name="AIAgentProps" id="@yike5460/intelli-agent.AIAgentProps"></a>

#### Initializer <a name="Initializer" id="@yike5460/intelli-agent.AIAgentProps.Initializer"></a>

```typescript
import { AIAgentProps } from '@yike5460/intelli-agent'

const aIAgentProps: AIAgentProps = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#@yike5460/intelli-agent.AIAgentProps.property.agentName">agentName</a></code> | <code>string</code> | The name of the AI agent. |
| <code><a href="#@yike5460/intelli-agent.AIAgentProps.property.memorySize">memorySize</a></code> | <code>number</code> | The memory size for the Lambda function. |
| <code><a href="#@yike5460/intelli-agent.AIAgentProps.property.runtime">runtime</a></code> | <code>aws-cdk-lib.aws_lambda.Runtime</code> | The runtime for the Lambda function. |

---

##### `agentName`<sup>Required</sup> <a name="agentName" id="@yike5460/intelli-agent.AIAgentProps.property.agentName"></a>

```typescript
public readonly agentName: string;
```

- *Type:* string

The name of the AI agent.

---

##### `memorySize`<sup>Optional</sup> <a name="memorySize" id="@yike5460/intelli-agent.AIAgentProps.property.memorySize"></a>

```typescript
public readonly memorySize: number;
```

- *Type:* number
- *Default:* 128

The memory size for the Lambda function.

---

##### `runtime`<sup>Optional</sup> <a name="runtime" id="@yike5460/intelli-agent.AIAgentProps.property.runtime"></a>

```typescript
public readonly runtime: Runtime;
```

- *Type:* aws-cdk-lib.aws_lambda.Runtime
- *Default:* lambda.Runtime.NODEJS_18_X

The runtime for the Lambda function.

---



