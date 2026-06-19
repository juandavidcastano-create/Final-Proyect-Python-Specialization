"""
Lambda function para calcular y actualizar tamaño de documentos.

Disparado por: S3 PutObject event
Acciones:
  1. Obtiene metadata del objeto S3 (tamaño)
  2. Busca el documento en la BD
  3. Actualiza el tamaño del documento si cambió
"""

import json
import boto3
import os
import psycopg2

s3_client = boto3.client('s3')
bucket_name = os.environ.get('S3_BUCKET_NAME', 'project-documents')


def get_db_connection():
    """Crear conexión a PostgreSQL."""
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'postgres'),
        database=os.environ.get('DB_NAME', 'project_db'),
        port=int(os.environ.get('DB_PORT', 5432))
    )
    return conn


def get_document_id_from_s3_key(s3_key, bucket):
    """
    Obtener document_id consultando la BD.
    
    s3_key estructura: owner_id/project_id/file_name
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id FROM document WHERE s3_key = %s
        """, (s3_key,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return result[0] if result else None
    except Exception as e:
        print(f"Error obteniendo document_id: {e}")
        return None


def get_s3_object_size(bucket, key):
    """Obtener tamaño del objeto en S3."""
    try:
        response = s3_client.head_object(Bucket=bucket, Key=key)
        return response['ContentLength']
    except Exception as e:
        print(f"Error obteniendo tamaño de S3: {e}")
        raise


def update_document_size(document_id, size):
    """Actualizar tamaño del documento en la BD."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE document
            SET size = %s
            WHERE id = %s
        """, (size, document_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Tamaño del documento {document_id} actualizado a {size} bytes")
        return True
    except Exception as e:
        print(f"Error actualizando tamaño en BD: {e}")
        return False


def lambda_handler(event, context):
    """
    Handler principal.
    
    event estructura:
    {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "bucket-name"},
                    "object": {"key": "1/1/document.pdf", "size": 102400}
                }
            }
        ]
    }
    """
    try:
        print(f"Evento recibido: {json.dumps(event)}")
        
        for record in event.get('Records', []):
            s3_info = record.get('s3', {})
            bucket = s3_info.get('bucket', {}).get('name', bucket_name)
            key = s3_info.get('object', {}).get('key', '')
            size = s3_info.get('object', {}).get('size')
            
            if not key:
                print("No se encontró key en el evento")
                continue
            
            print(f"Procesando: s3://{bucket}/{key}, tamaño: {size} bytes")
            
            # Obtener document_id de la BD
            document_id = get_document_id_from_s3_key(key, bucket)
            if not document_id:
                print(f"Documento no encontrado para key: {key}")
                continue
            
            # Obtener tamaño real de S3
            actual_size = get_s3_object_size(bucket, key)
            print(f"Tamaño real en S3: {actual_size} bytes")
            
            # Actualizar en BD
            if update_document_size(document_id, actual_size):
                print(f"Documento {document_id} actualizado exitosamente")
            else:
                print(f"Error actualizando documento {document_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Tamaños actualizados exitosamente')
        }
    
    except Exception as e:
        print(f"Error en lambda_handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
