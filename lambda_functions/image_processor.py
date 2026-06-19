"""
Lambda function for processing images: redimensionar y extraer metadata.

Disparado por: S3 PutObject event
Acciones:
  1. Descarga la imagen de S3
  2. Redimensiona a thumbnail (200x200)
  3. Guarda thumbnail en S3 con sufijo _thumb
  4. Extrae metadata (resolución, tamaño, formato)
  5. Actualiza metadata en DB (opcional)
"""

import json
import boto3
import os
from PIL import Image
from io import BytesIO
import psycopg2
from psycopg2.extras import RealDictCursor

s3_client = boto3.client('s3')
bucket_name = os.environ.get('S3_BUCKET_NAME', 'project-documents')

# Database connection
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


def download_image_from_s3(bucket, key):
    """Descargar imagen de S3."""
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        return response['Body'].read()
    except Exception as e:
        print(f"Error descargando imagen: {e}")
        raise


def create_thumbnail(image_content):
    """Crear thumbnail de la imagen."""
    try:
        image = Image.open(BytesIO(image_content))
        
        # Resize to 200x200
        image.thumbnail((200, 200), Image.Resampling.LANCZOS)
        
        # Save to BytesIO
        thumb_io = BytesIO()
        image.save(thumb_io, format='JPEG')
        thumb_io.seek(0)
        
        return thumb_io.getvalue()
    except Exception as e:
        print(f"Error creando thumbnail: {e}")
        raise


def upload_to_s3(bucket, key, content):
    """Subir archivo a S3."""
    try:
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=content,
            ContentType='image/jpeg'
        )
        return True
    except Exception as e:
        print(f"Error subiendo a S3: {e}")
        raise


def extract_image_metadata(image_content):
    """Extraer metadata de la imagen."""
    try:
        image = Image.open(BytesIO(image_content))
        return {
            'width': image.width,
            'height': image.height,
            'format': image.format,
            'size_bytes': len(image_content)
        }
    except Exception as e:
        print(f"Error extrayendo metadata: {e}")
        raise


def update_document_metadata(document_id, metadata):
    """Actualizar metadata del documento en la BD (opcional)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ejemplo: crear tabla de metadata si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_metadata (
                document_id INT PRIMARY KEY,
                width INT,
                height INT,
                format VARCHAR(50),
                size_bytes INT,
                thumbnail_generated BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            INSERT INTO document_metadata (document_id, width, height, format, size_bytes, thumbnail_generated)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (document_id) DO UPDATE SET
                width = EXCLUDED.width,
                height = EXCLUDED.height,
                format = EXCLUDED.format,
                size_bytes = EXCLUDED.size_bytes,
                thumbnail_generated = TRUE
        """, (
            document_id,
            metadata['width'],
            metadata['height'],
            metadata['format'],
            metadata['size_bytes']
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Metadata actualizada para documento {document_id}")
    except Exception as e:
        print(f"Error actualizando metadata en DB: {e}")
        # No fallar si la BD no está disponible


def lambda_handler(event, context):
    """
    Handler principal de Lambda.
    
    event estructura:
    {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "bucket-name"},
                    "object": {"key": "1/1/image.jpg"}
                }
            }
        ]
    }
    """
    try:
        print(f"Evento recibido: {json.dumps(event)}")
        
        # Procesar cada record del evento
        for record in event.get('Records', []):
            s3_info = record.get('s3', {})
            bucket = s3_info.get('bucket', {}).get('name', bucket_name)
            key = s3_info.get('object', {}).get('key', '')
            
            if not key:
                print("No se encontró key en el evento")
                continue
            
            print(f"Procesando: s3://{bucket}/{key}")
            
            # Descargar imagen
            image_content = download_image_from_s3(bucket, key)
            print(f"Imagen descargada, tamaño: {len(image_content)} bytes")
            
            # Extraer metadata
            metadata = extract_image_metadata(image_content)
            print(f"Metadata extraída: {metadata}")
            
            # Crear thumbnail
            thumbnail_content = create_thumbnail(image_content)
            print(f"Thumbnail creado, tamaño: {len(thumbnail_content)} bytes")
            
            # Subir thumbnail a S3
            thumbnail_key = key.replace('.jpg', '_thumb.jpg').replace('.png', '_thumb.png')
            upload_to_s3(bucket, thumbnail_key, thumbnail_content)
            print(f"Thumbnail subido a: s3://{bucket}/{thumbnail_key}")
            
            # Actualizar metadata en DB (opcional)
            # Extraer document_id de la key (ej: 1/1/image.jpg -> document_id=1)
            try:
                # Aquí asumimos que el key contiene owner_id/project_id/filename
                # En un caso real, deberías consultar la BD para obtener el document_id
                # document_id = get_document_id_from_s3_key(key)
                # update_document_metadata(document_id, metadata)
                pass
            except Exception as e:
                print(f"No se pudo actualizar metadata en DB: {e}")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Imágenes procesadas exitosamente')
        }
    
    except Exception as e:
        print(f"Error en lambda_handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
