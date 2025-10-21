# Novi PQR - Ejemplo de Estructura CDK

## Estructura de Archivos
```
novi-backend/
├── cdk/
│   ├── app.ts                 # Punto de entrada CDK
│   ├── lib/
│   │   └── novi-pqr-stack.ts  # Stack principal
│   ├── lambda/
│   │   ├── create-pqr/
│   │   │   ├── create_pqr.py
│   │   │   └── requirements.txt
│   │   ├── check-pqr/
│   │   │   ├── check_pqr.py
│   │   │   └── requirements.txt
│   │   ├── invoke-agent/
│   │   │   ├── invoke_agent.py
│   │   │   └── requirements.txt
│   │   └── process-faqs/
│   │       ├── process_faqs.py
│   │       └── requirements.txt
│   ├── package.json
│   ├── tsconfig.json
│   └── cdk.json
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

## Comandos de Uso
```bash
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
