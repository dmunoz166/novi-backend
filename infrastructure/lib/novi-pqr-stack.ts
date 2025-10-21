import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

export class NoviPqrStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Tabla DynamoDB para almacenar PQRs
    const pqrTable = new dynamodb.Table(this, 'PqrTable', {
      tableName: 'novi-pqr-table',
      partitionKey: { name: 'pqr_id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Bucket S3 para FAQs (referencia al existente)
    const faqsBucket = s3.Bucket.fromBucketName(this, 'FaqsBucket', 'novi-pqr-faqs-bucket');

    // Rol IAM para las funciones Lambda
    const lambdaRole = new iam.Role(this, 'NoviLambdaRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
      ],
      inlinePolicies: {
        NoviPermissions: new iam.PolicyDocument({
          statements: [
            // DynamoDB
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: ['dynamodb:GetItem', 'dynamodb:PutItem', 'dynamodb:UpdateItem'],
              resources: [pqrTable.tableArn],
            }),
            // Bedrock
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: [
                'bedrock-agent-runtime:InvokeAgent',
                'bedrock-agent:*',
                'bedrock:*'
              ],
              resources: ['*'],
            }),
            // S3
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: ['s3:GetObject', 's3:ListBucket'],
              resources: [faqsBucket.bucketArn, `${faqsBucket.bucketArn}/*`]
            })
          ],
        }),
      },
    });

    // Rol IAM para Bedrock Agent
    const bedrockAgentRole = new iam.Role(this, 'BedrockAgentRole', {
      assumedBy: new iam.ServicePrincipal('bedrock.amazonaws.com'),
      inlinePolicies: {
        LambdaInvokePolicy: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: ['lambda:InvokeFunction'],
              resources: [`arn:aws:lambda:${this.region}:${this.account}:function:novi-bedrock-actions`]
            })
          ]
        })
      }
    });

    // Lambda: bedrock-actions (unificada)
    const bedrockActionsLambda = new lambda.Function(this, 'BedrockActionsFunction', {
      functionName: 'novi-bedrock-actions',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'bedrock_actions.handler',
      code: lambda.Code.fromAsset('../lambda-functions', {
        bundling: {
          image: lambda.Runtime.PYTHON_3_12.bundlingImage,
          command: [
            'bash', '-c',
            'cp -r /asset-input/* /asset-output/ && pip install --no-cache-dir -r /asset-output/requirements.txt -t /asset-output/ || echo "No requirements.txt found"'
          ],
        },
      }),
      role: lambdaRole,
      environment: {
        'PQR_TABLE_NAME': pqrTable.tableName,
        'REGION': 'us-west-2'
      },
      timeout: cdk.Duration.seconds(30),
    });

    // Lambda: invoke-agent
    const invokeAgentLambda = new lambda.Function(this, 'InvokeAgentFunction', {
      functionName: 'novi-invoke-agent',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'invoke_agent.lambda_handler',
      code: lambda.Code.fromAsset('../lambda-functions', {
        bundling: {
          image: lambda.Runtime.PYTHON_3_12.bundlingImage,
          command: [
            'bash', '-c',
            'cp -r /asset-input/* /asset-output/ && pip install --no-cache-dir -r /asset-output/requirements.txt -t /asset-output/ || echo "No requirements.txt found"'
          ],
        },
      }),
      role: lambdaRole,
      environment: {
        'BEDROCK_AGENT_ID': 'PLACEHOLDER', // Se actualiza después
        'BEDROCK_AGENT_ALIAS_ID': 'PLACEHOLDER',
        'REGION': 'us-west-2'
      },
      timeout: cdk.Duration.seconds(60),
    });

    // API Gateway
    const api = new apigateway.RestApi(this, 'NoviPqrApi', {
      restApiName: 'novi-pqr-api',
      description: 'API para gestión de PQRs de Novi',
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
      },
    });

    // Endpoint principal: POST /agent
    const agentResource = api.root.addResource('agent');
    agentResource.addMethod('POST', new apigateway.LambdaIntegration(invokeAgentLambda));

    // Outputs
    new cdk.CfnOutput(this, 'ApiUrl', {
      value: api.url,
      description: 'URL de la API'
    });

    new cdk.CfnOutput(this, 'TableName', {
      value: pqrTable.tableName,
      description: 'Nombre de la tabla DynamoDB'
    });

    new cdk.CfnOutput(this, 'BedrockAgentRoleArn', {
      value: bedrockAgentRole.roleArn,
      description: 'ARN del rol para Bedrock Agent - usar en setup_agent.py'
    });

    new cdk.CfnOutput(this, 'SetupCommand', {
      value: `cd ../scripts && BEDROCK_AGENT_ROLE_ARN=${bedrockAgentRole.roleArn} python3 setup_agent.py`,
      description: 'Comando para configurar el agente después del deploy'
    });
  }
}
