"""
Rotas para upload e gestão de arquivos (imagens)
"""
import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, Form
from src.utils.dependencies import require_role, AuthenticatedUser
from PIL import Image
import io


router = APIRouter(prefix="/files", tags=["files"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "uploads")
UPLOAD_DIR = os.path.abspath(UPLOAD_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", dependencies=[Depends(require_role("admin"))])
async def upload_image(file: UploadFile = File(...)):
    """Upload de imagens - Acesso apenas para admin"""
    try:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Arquivo deve ser uma imagem")

        ext = os.path.splitext(file.filename or "")[1].lower() or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        dest_path = os.path.join(UPLOAD_DIR, filename)

        with open(dest_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # URL pública servida pelo StaticFiles montado em /uploads
        public_url = f"/uploads/{filename}"
        return {"url": public_url, "filename": filename}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro no upload: {str(e)}")


@router.post("/upload-with-transform", dependencies=[Depends(require_role("admin"))])
async def upload_image_with_transform(
    file: UploadFile = File(...),
    zoom: float = Form(1.0),
    offset_x: float = Form(0.0),
    offset_y: float = Form(0.0)
):
    """Upload de imagens com transformações aplicadas - Acesso apenas para admin"""
    try:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Arquivo deve ser uma imagem")

        # Ler o conteúdo da imagem
        content = await file.read()
        
        # Abrir a imagem com PIL
        image = Image.open(io.BytesIO(content))
        
        # Converter para RGB se necessário (para JPEG)
        if image.mode in ('RGBA', 'LA', 'P'):
            # Criar fundo branco para imagens com transparência
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Aplicar transformações
        if zoom != 1.0 or offset_x != 0.0 or offset_y != 0.0:
            # Calcular novo tamanho baseado no zoom
            new_width = int(image.width * zoom)
            new_height = int(image.height * zoom)
            
            # Redimensionar a imagem
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Calcular área de corte (crop) baseada no offset
            crop_x = max(0, int(offset_x))
            crop_y = max(0, int(offset_y))
            crop_width = min(new_width - crop_x, image.width)
            crop_height = min(new_height - crop_y, image.height)
            
            # Se a imagem redimensionada é menor que a original, centralizar
            if new_width < image.width or new_height < image.height:
                # Criar uma nova imagem com o tamanho original
                final_image = Image.new('RGB', (image.width, image.height), (255, 255, 255))
                paste_x = max(0, (image.width - new_width) // 2)
                paste_y = max(0, (image.height - new_height) // 2)
                final_image.paste(resized_image, (paste_x, paste_y))
                image = final_image
            else:
                # Cortar a parte central da imagem redimensionada
                left = crop_x
                top = crop_y
                right = left + image.width
                bottom = top + image.height
                image = resized_image.crop((left, top, right, bottom))

        # Salvar a imagem processada
        ext = os.path.splitext(file.filename or "")[1].lower() or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        dest_path = os.path.join(UPLOAD_DIR, filename)
        
        # Salvar no formato apropriado
        if ext.lower() in ['.png']:
            image.save(dest_path, 'PNG', quality=95)
        else:
            image.save(dest_path, 'JPEG', quality=95)

        # URL pública servida pelo StaticFiles montado em /uploads
        public_url = f"/uploads/{filename}"
        return {"url": public_url, "filename": filename}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro no upload com transformação: {str(e)}")


