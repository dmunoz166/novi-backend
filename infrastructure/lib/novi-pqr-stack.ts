import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

export class NoviPqrStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Tabla DynamoDB para almacenar PQRs - configuración simple
    const pqrTable = new dynamodb.Table(this, 'PqrTable', {
      tableName: 'novi-pqr-table',
      partitionKey: { name: 'pqr_id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST, // Simplicidad: sin provisioning
      removalPolicy: cdk.RemovalPolicy.DESTROY, // Para MVP, permitir destrucción
    });

    // Rol IAM para las funciones Lambda - permisos básicos
    const lambdaRole = new iam.Role(this, 'NoviLambdaRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
      ],
      inlinePolicies: {
        DynamoDBAccess: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: [
                'dynamodb:GetItem',
                'dynamodb:PutItem',
                'dynamodb:UpdateItem',
                'dynamodb:Query',
                'dynamodb:Scan'
              ],
              resources: [pqrTable.tableArn],
            }),
          ],
        }),
        BedrockAccess: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: [
                'bedrock:InvokeModel',
                'bedrock-agent:InvokeAgent',
                'bedrock-agent:GetAgent',
                'bedrock-agent:ListAgents'
              ],
              resources: ['*'], // Simplicidad: permisos amplios para MVP
            }),
          ],
        }),
      },
    });

    // Lambda para crear PQR
    const createPqrLambda = new lambda.Function(this, 'CreatePqrFunction', {
      functionName: 'novi-create-pqr',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'create_pqr.handler',
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

    // Lambda para consultar PQR
    const checkPqrLambda = new lambda.Function(this, 'CheckPqrFunction', {
      functionName: 'novi-check-pqr',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'check_pqr.handler',
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

    // API Gateway REST API - configuración simple
    const api = new apigateway.RestApi(this, 'NoviPqrApi', {
      restApiName: 'novi-pqr-api',
      description: 'API para gestión de PQRs de Novi',
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS, // Simplicidad: CORS abierto para MVP
        allowMethods: apigateway.Cors.ALL_METHODS,
      },
    });

    // Endpoints de la API
    const pqrResource = api.root.addResource('pqr');
    
    // POST /pqr - crear PQR
    pqrResource.addMethod('POST', new apigateway.LambdaIntegration(createPqrLambda));
    
    // GET /pqr/{pqr_id} - consultar PQR
    const pqrIdResource = pqrResource.addResource('{pqr_id}');
    pqrIdResource.addMethod('GET', new apigateway.LambdaIntegration(checkPqrLambda));

    // Outputs para facilitar testing
    new cdk.CfnOutput(this, 'ApiUrl', {
      value: api.url,
      description: 'URL base de la API de Novi PQR',
    });

    new cdk.CfnOutput(this, 'PqrTableName', {
      value: pqrTable.tableName,
      description: 'Nombre de la tabla DynamoDB para PQRs',
    });
  }
}
