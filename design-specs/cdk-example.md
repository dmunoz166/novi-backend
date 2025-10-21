# Novi PQR - Ejemplo de Estructura CDK (Actualizado con Bedrock Agent)

## Estructura de Archivos
```
novi-backend/
├── cdk/
│   ├── app.ts                 # Punto de entrada CDK
│   ├── lib/
│   │   └── novi-pqr-stack.ts  # Stack principal con Bedrock Agent
│   ├── lambda/
│   │   ├── invoke-agent/
│   │   │   ├── invoke_agent.py
│   │   │   └── requirements.txt
│   │   └── bedrock-actions/
│   │       ├── bedrock_actions.py
│   │       └── requirements.txt
│   ├── schemas/
│   │   └── pqr-openapi-schema.yaml  # OpenAPI para Action Groups
│   ├── package.json
│   ├── tsconfig.json
│   └── cdk.json
├── scripts/
│   └── setup_agent.py              # Script unificado de configuración
└── faqs-novi.csv                   # FAQs para integración
```

## app.ts
```typescript
#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { NoviPqrStack } from './lib/novi-pqr-stack';

const app = new cdk.App();
new NoviPqrStack(app, 'NoviPqrStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: 'us-west-2'
  }
});
```

## package.json
```json
{
  "name": "novi-pqr-cdk",
  "version": "1.0.0",
  "main": "lib/app.js",
  "scripts": {
    "build": "tsc",
    "watch": "tsc -w",
    "test": "jest",
    "cdk": "cdk"
  },
  "devDependencies": {
    "@types/jest": "^29.4.0",
    "@types/node": "18.14.6",
    "jest": "^29.5.0",
    "ts-jest": "^29.0.5",
    "aws-cdk": "2.87.0",
    "ts-node": "^10.9.1",
    "typescript": "~4.9.5"
  },
  "dependencies": {
    "aws-cdk-lib": "2.87.0",
    "constructs": "^10.0.0",
    "source-map-support": "^0.5.21"
  }
}
```

## cdk.json
```json
{
  "app": "npx ts-node --prefer-ts-exts app.ts",
  "watch": {
    "include": [
      "**"
    ],
    "exclude": [
      "README.md",
      "cdk*.json",
      "**/*.d.ts",
      "**/*.js",
      "tsconfig.json",
      "package*.json",
      "yarn.lock",
      "node_modules",
      "test"
    ]
  },
  "context": {
    "@aws-cdk/aws-lambda:recognizeLayerVersion": true,
    "@aws-cdk/core:checkSecretUsage": true,
    "@aws-cdk/core:target-partitions": ["aws", "aws-cn"]
  }
}
```

## lib/novi-pqr-stack.ts (Actualizado con Bedrock Agent)
```typescript
import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as bedrock from 'aws-cdk-lib/aws-bedrock';

export class NoviPqrStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // ... recursos existentes (DynamoDB, Lambda, API Gateway) ...

    // S3 Bucket para OpenAPI Schema
    const openApiSchemaBucket = new s3.Bucket(this, 'OpenApiSchemaBucket', {
      bucketName: 'novi-pqr-openapi-schemas',
      versioned: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN
    });

    // IAM Role para Bedrock Agent
    const bedrockAgentRole = new iam.Role(this, 'BedrockAgentRole', {
      assumedBy: new iam.ServicePrincipal('bedrock.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonBedrockFullAccess')
      ],
      inlinePolicies: {
        LambdaInvokePolicy: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: ['lambda:InvokeFunction'],
              resources: [createPqrFunction.functionArn, checkPqrFunction.functionArn]
            })
          ]
        })
      }
    });

    // Bedrock Agent usando CloudFormation nativo
    const bedrockAgent = new bedrock.CfnAgent(this, 'NoviAgent', {
      agentName: 'novi-pqr-agent',
      description: 'Agente para gestión de PQR de NovaMarket',
      foundationModel: 'anthropic.claude-3-5-sonnet-20241022-v2:0',
      instruction: `Eres Novi, asistente de PQR para NovaMarket.
Tu función es ayudar a crear PQR y consultar su estado.
Mantén un tono profesional y empático.`,
      agentResourceRoleArn: bedrockAgentRole.roleArn,
      autoPrepare: true,
      actionGroups: [{
        actionGroupName: 'pqr-actions',
        description: 'Acciones para crear y consultar PQR',
        apiSchema: {
          s3: {
            s3BucketName: openApiSchemaBucket.bucketName,
            s3ObjectKey: 'pqr-openapi-schema.yaml'
          }
        },
        actionGroupExecutor: {
          lambda: createPqrFunction.functionArn
        }
      }]
    });

    // Outputs
    new cdk.CfnOutput(this, 'BedrockAgentId', {
      value: bedrockAgent.attrAgentId,
      description: 'ID del agente Bedrock'
    });
  }
}
```

## Comandos de Uso
# Inicializar proyecto
npm install

# Compilar TypeScript
npm run build

# Sintetizar CloudFormation
cdk synth

# Desplegar
cdk deploy

# Destruir (solo desarrollo)
cdk destroy
```
