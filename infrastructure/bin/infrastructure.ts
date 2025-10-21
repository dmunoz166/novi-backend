#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { NoviPqrStack } from '../lib/novi-pqr-stack';

const app = new cdk.App();

// Configuración hardcodeada para MVP - simplicidad primero
new NoviPqrStack(app, 'NoviPqrStack', {
  env: { 
    account: '436187211477', 
    region: 'us-west-2' 
  },
});