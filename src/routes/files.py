"""
Rotas para upload e gestão de arquivos (imagens)
"""
import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from src.utils.dependencies import require_role, AuthenticatedUser


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


