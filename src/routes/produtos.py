"""
Rotas para gerenciamento de produtos
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from src.models.produto import Produto, Acompanhamento
from src.models.categoria import Categoria

router = APIRouter(prefix="/produtos", tags=["produtos"])

@router.get("/", response_model=List[dict])
async def get_produtos():
    """Listar todos os produtos"""
    try:
        produtos = Produto.objects()
        return [produto.to_dict() for produto in produtos]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar produtos: {str(e)}"
        )

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_produto(produto_data: dict):
    """Criar novo produto"""
    try:
        # Validar campos obrigatórios
        required_fields = ['categoria_id', 'titulo', 'preco']
        for field in required_fields:
            if not produto_data.get(field):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Campo '{field}' é obrigatório"
                )
        
        # Verificar se a categoria existe
        categoria = Categoria.objects(id=produto_data['categoria_id']).first()
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Categoria não encontrada"
            )
        
        # Processar acompanhamentos se fornecidos
        acompanhamentos = []
        if produto_data.get('acompanhamentos'):
            for acomp_data in produto_data['acompanhamentos']:
                acompanhamento = Acompanhamento(
                    nome=acomp_data['nome'],
                    preco=acomp_data['preco']
                )
                acompanhamentos.append(acompanhamento)
        
        # Criar produto
        produto = Produto(
            categoria=categoria,
            titulo=produto_data['titulo'],
            descricao_capa=produto_data.get('descricao_capa'),
            descricao_geral=produto_data.get('descricao_geral'),
            preco=produto_data['preco'],
            preco_promocional=produto_data.get('preco_promocional'),
            status=produto_data.get('status', 'Ativo'),
            estrelas_kaiserhaus=produto_data.get('estrelas_kaiserhaus', False),
            acompanhamentos=acompanhamentos
        )
        
        produto.save()
        return produto.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar produto: {str(e)}"
        )

@router.get("/{produto_id}", response_model=dict)
async def get_produto(produto_id: str):
    """Buscar produto por ID"""
    try:
        produto = Produto.objects(id=produto_id).first()
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado"
            )
        return produto.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar produto: {str(e)}"
        )

@router.put("/{produto_id}", response_model=dict)
async def update_produto(produto_id: str, produto_data: dict):
    """Atualizar produto"""
    try:
        produto = Produto.objects(id=produto_id).first()
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado"
            )
        
        # Atualizar categoria se fornecida
        if produto_data.get('categoria_id'):
            categoria = Categoria.objects(id=produto_data['categoria_id']).first()
            if not categoria:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Categoria não encontrada"
                )
            produto.categoria = categoria
        
        # Atualizar outros campos
        for field, value in produto_data.items():
            if field == 'categoria_id':
                continue
            elif field == 'acompanhamentos' and value:
                acompanhamentos = []
                for acomp_data in value:
                    acompanhamento = Acompanhamento(
                        nome=acomp_data['nome'],
                        preco=acomp_data['preco']
                    )
                    acompanhamentos.append(acompanhamento)
                produto.acompanhamentos = acompanhamentos
            elif hasattr(produto, field):
                setattr(produto, field, value)
        
        produto.save()
        return produto.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar produto: {str(e)}"
        )

@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_produto(produto_id: str):
    """Deletar produto"""
    try:
        produto = Produto.objects(id=produto_id).first()
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado"
            )
        
        produto.delete()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar produto: {str(e)}"
        )

@router.get("/categoria/{categoria_id}", response_model=List[dict])
async def listar_produtos_por_categoria(categoria_id: str):
    """Listar produtos por categoria"""
    try:
        categoria = Categoria.objects(id=categoria_id).first()
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada"
            )
        
        produtos = Produto.objects(categoria=categoria)
        return [produto.to_dict() for produto in produtos]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar produtos por categoria: {str(e)}"
        )

@router.get("/estrelas-kaiserhaus", response_model=List[dict])
async def listar_estrelas_kaiserhaus():
    """Listar produtos que fazem parte das estrelas da Kaiserhaus"""
    try:
        produtos = Produto.objects(estrelas_kaiserhaus=True)
        return [produto.to_dict() for produto in produtos]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar estrelas da Kaiserhaus: {str(e)}"
        )
