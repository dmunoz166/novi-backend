#!/usr/bin/env python3
"""
Tests básicos para la función create-pqr
Siguiendo principio de simplicidad-first
"""

import json
import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Agregar el directorio de lambda-functions al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda-functions'))

# Importar la función a testear
from create_pqr import handler

class TestCreatePqr(unittest.TestCase):
    """Tests básicos para create-pqr"""
    
    def setUp(self):
        """Setup para cada test"""
        # Mock de variables de entorno
        os.environ['PQR_TABLE_NAME'] = 'test-table'
    
    @patch('create_pqr.table')
    def test_create_pqr_success(self, mock_table):
        """Test caso exitoso de creación de PQR"""
        # Configurar mock
        mock_table.put_item.return_value = {}
        
        # Evento de prueba
        event = {
            'body': json.dumps({
                'customer_email': 'test@example.com',
                'description': 'Test description',
                'priority': 'ALTA',
                'category': 'TEST'
            })
        }
        
        # Ejecutar función
        result = handler(event, {})
        
        # Verificar resultado
        self.assertEqual(result['statusCode'], 200)
        
        # Verificar que se llamó put_item
        mock_table.put_item.assert_called_once()
        
        # Verificar estructura de respuesta
        body = json.loads(result['body'])
        self.assertIn('message', body)
        self.assertIn('pqr_id', body)
        self.assertIn('status', body)
        self.assertEqual(body['status'], 'CREADA')
    
    def test_create_pqr_missing_email(self):
        """Test error por email faltante"""
        event = {
            'body': json.dumps({
                'description': 'Test description'
            })
        }
        
        result = handler(event, {})
        
        self.assertEqual(result['statusCode'], 400)
        body = json.loads(result['body'])
        self.assertIn('error', body)
        self.assertIn('customer_email', body['error'])
    
    def test_create_pqr_missing_description(self):
        """Test error por descripción faltante"""
        event = {
            'body': json.dumps({
                'customer_email': 'test@example.com'
            })
        }
        
        result = handler(event, {})
        
        self.assertEqual(result['statusCode'], 400)
        body = json.loads(result['body'])
        self.assertIn('error', body)
        self.assertIn('description', body['error'])
    
    def test_create_pqr_invalid_json(self):
        """Test error por JSON inválido"""
        event = {
            'body': 'invalid json'
        }
        
        result = handler(event, {})
        
        self.assertEqual(result['statusCode'], 400)
        body = json.loads(result['body'])
        self.assertIn('error', body)
        self.assertIn('JSON inválido', body['error'])
    
    @patch('create_pqr.table')
    def test_create_pqr_dynamodb_error(self, mock_table):
        """Test error de DynamoDB"""
        # Configurar mock para lanzar excepción
        mock_table.put_item.side_effect = Exception('DynamoDB error')
        
        event = {
            'body': json.dumps({
                'customer_email': 'test@example.com',
                'description': 'Test description'
            })
        }
        
        result = handler(event, {})
        
        self.assertEqual(result['statusCode'], 500)
        body = json.loads(result['body'])
        self.assertIn('error', body)

if __name__ == '__main__':
    print("Ejecutando tests para create-pqr...")
    unittest.main(verbosity=2)
