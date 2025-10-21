#!/usr/bin/env python3
"""
Tests básicos para la función check-pqr
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
from check_pqr import handler

class TestCheckPqr(unittest.TestCase):
    """Tests básicos para check-pqr"""
    
    def setUp(self):
        """Setup para cada test"""
        # Mock de variables de entorno
        os.environ['PQR_TABLE_NAME'] = 'test-table'
    
    @patch('check_pqr.table')
    def test_check_pqr_found(self, mock_table):
        """Test caso exitoso - PQR encontrada"""
        # Configurar mock
        mock_table.get_item.return_value = {
            'Item': {
                'pqr_id': 'test-123',
                'customer_email': 'test@example.com',
                'description': 'Test description',
                'status': 'CREADA',
                'priority': 'MEDIA',
                'category': 'GENERAL',
                'created_at': '2025-10-21T18:00:00',
                'updated_at': '2025-10-21T18:00:00'
            }
        }
        
        # Evento de prueba
        event = {
            'pathParameters': {
                'pqr_id': 'test-123'
            }
        }
        
        # Ejecutar función
        result = handler(event, {})
        
        # Verificar resultado
        self.assertEqual(result['statusCode'], 200)
        
        # Verificar que se llamó get_item
        mock_table.get_item.assert_called_once_with(
            Key={'pqr_id': 'test-123'}
        )
        
        # Verificar estructura de respuesta
        body = json.loads(result['body'])
        self.assertIn('message', body)
        self.assertIn('pqr', body)
        self.assertEqual(body['pqr']['pqr_id'], 'test-123')
    
    @patch('check_pqr.table')
    def test_check_pqr_not_found(self, mock_table):
        """Test PQR no encontrada"""
        # Configurar mock - sin Item
        mock_table.get_item.return_value = {}
        
        event = {
            'pathParameters': {
                'pqr_id': 'inexistente'
            }
        }
        
        result = handler(event, {})
        
        self.assertEqual(result['statusCode'], 404)
        body = json.loads(result['body'])
        self.assertIn('error', body)
        self.assertIn('no encontrada', body['error'])
    
    def test_check_pqr_missing_id(self):
        """Test error por ID faltante"""
        event = {
            'pathParameters': None
        }
        
        result = handler(event, {})
        
        self.assertEqual(result['statusCode'], 400)
        body = json.loads(result['body'])
        self.assertIn('error', body)
        self.assertIn('pqr_id', body['error'])
    
    def test_check_pqr_empty_path_parameters(self):
        """Test error por pathParameters vacío"""
        event = {
            'pathParameters': {}
        }
        
        result = handler(event, {})
        
        self.assertEqual(result['statusCode'], 400)
        body = json.loads(result['body'])
        self.assertIn('error', body)
        self.assertIn('pqr_id', body['error'])
    
    @patch('check_pqr.table')
    def test_check_pqr_dynamodb_error(self, mock_table):
        """Test error de DynamoDB"""
        from botocore.exceptions import ClientError
        
        # Configurar mock para lanzar excepción
        mock_table.get_item.side_effect = ClientError(
            {'Error': {'Code': 'ValidationException', 'Message': 'Test error'}},
            'GetItem'
        )
        
        event = {
            'pathParameters': {
                'pqr_id': 'test-123'
            }
        }
        
        result = handler(event, {})
        
        self.assertEqual(result['statusCode'], 500)
        body = json.loads(result['body'])
        self.assertIn('error', body)

if __name__ == '__main__':
    print("Ejecutando tests para check-pqr...")
    unittest.main(verbosity=2)
