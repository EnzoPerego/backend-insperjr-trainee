"""
Serviço de Email para Kaiserhaus
Responsável pelo envio de emails de recuperação de senha
"""

import os
from pathlib import Path
from typing import Optional
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi import HTTPException
import logging
from datetime import datetime


logger = logging.getLogger(__name__)

class EmailService:
    
    def __init__(self):
        self.config = ConnectionConfig(
            MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
            MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
            MAIL_FROM=os.getenv("MAIL_FROM"),
            MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
            MAIL_SERVER=os.getenv("MAIL_SERVER"),
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        self.fastmail = FastMail(self.config)
    
    async def send_password_reset_email(
        self, 
        email: str, 
        token: str, 
        user_type: str
    ) -> bool:
        """
    
            a ideia seria retornar um valorr booleano  , pois esria true se enviado com sucesso, false caso contrário
        """
        try:
            subject = "Recuperação de Senha - Kaiserhaus"
            
            # url para reset usando variável de ambiente
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
            reset_url = f"{frontend_url}/redefinir-senha?token={token}"
            
            html_body = self._create_reset_email_template(
                email=email,
                token=token,
                reset_url=reset_url,
                user_type=user_type
            )
            
            text_body = self._create_reset_email_text(
                email=email,
                token=token,
                reset_url=reset_url,
                user_type=user_type
            )
            
            message = MessageSchema(
                subject=subject,
                recipients=[email],
                body=html_body,
                subtype="html"
            )
            
            # aqui eh o envio do email
            await self.fastmail.send_message(message)
            
            logger.info(f"Email de reset enviado com sucesso para: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email de reset para {email}: {str(e)}")
            return False
    
    async def enviar_email_registro(
        self,
        email: str,
        nome: str,
        senha_temporaria: str,
        role: str
    ) -> bool:
        """
        Envia email de boas-vindas para novo funcionário com senha temporária

        
        """
        try:
            subject = "Bem-vindo ao Kaiserhaus - Sua Conta Foi Criada"
            
            # URL para login e redefinição
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
            login_url = f"{frontend_url}/login"
            
            html_body = self._criar_template_email_registro(
                email=email,
                nome=nome,
                senha_temporaria=senha_temporaria,
                role=role,
                login_url=login_url
            )
            
            text_body = self._criar_texto_email_registro(
                email=email,
                nome=nome,
                senha_temporaria=senha_temporaria,
                role=role,
                login_url=login_url
            )
            
            message = MessageSchema(
                subject=subject,
                recipients=[email],
                body=html_body,
                subtype="html"
            )
            
            await self.fastmail.send_message(message)
            
            logger.info(f"Email de boas-vindas enviado com sucesso para: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email de boas-vindas para {email}: {str(e)}")
            return False
    
    def _get_current_time(self) -> str:
        # data formatada
        now = datetime.now()
        return now.strftime("%d/%m/%Y às %H:%M")
    
    def _load_template(self, template_name: str) -> str:
        # carrega template HTML de arquivo
        template_path = Path(__file__).parent.parent / "templates" / template_name
        with open(template_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _create_reset_email_template(
        self, 
        email: str, 
        token: str, 
        reset_url: str, 
        user_type: str
    ) -> str:

        # carregar template
        template = self._load_template("email_reset_password.html")
        
        template = template.replace("{{ email }}", email)
        template = template.replace("{{ user_type }}", user_type.title())
        template = template.replace("{{ datetime }}", self._get_current_time())
        template = template.replace("{{ reset_url }}", reset_url)
        
        return template
    
    #caso so o email sem htmlfor enviado, por precaucao
    def _create_reset_email_text(
        self, 
        email: str, 
        token: str, 
        reset_url: str, 
        user_type: str
    ) -> str:
        return f"""
        KAISERHAUS - Recuperação de Senha

        Olá!
        
        Recebemos uma solicitação para redefinir a senha da sua conta no Kaiserhaus.
        Estamos aqui para ajudar você a recuperar o acesso à sua conta de forma segura.
        
        INFORMAÇÕES DA SOLICITAÇÃO:
        Email: {email}
        Tipo de conta: {user_type.title()}
        Data/Hora: {self._get_current_time()}
        
        Para redefinir sua senha, acesse este link:
        {reset_url}
        
        INFORMAÇÕES IMPORTANTES:
        - Este link expira em 1 hora por questões de segurança
        - O link pode ser usado apenas uma vez
        - Se você não solicitou esta alteração, ignore este email
        - Nunca compartilhe este link com outras pessoas
        
        Este é um email automático, não responda.
        
        KAISERHAUS
        © 2024 Kaiserhaus - Todos os direitos reservados
        Há mais de 40 anos em São Paulo
        """
    
    def _criar_template_email_registro(
        self,
        email: str,
        nome: str,
        senha_temporaria: str,
        role: str,
        login_url: str
    ) -> str:
        """Cria template HTML para email de boas-vindas"""
        template = self._load_template("email_de_registro.html")
        
        role_pt = {
            'admin': 'Administrador',
            'motoboy': 'Motoboy',
            'funcionario': 'Funcionário'
        }.get(role, 'Funcionário')
        
        template = template.replace("{{ nome }}", nome)
        template = template.replace("{{ email }}", email)
        template = template.replace("{{ role }}", role_pt)
        template = template.replace("{{ senha_temporaria }}", senha_temporaria)
        template = template.replace("{{ login_url }}", login_url)
        template = template.replace("{{ datetime }}", self._get_current_time())
        
        return template
    
    def _criar_texto_email_registro(
        self,
        email: str,
        nome: str,
        senha_temporaria: str,
        role: str,
        login_url: str
    ) -> str:
        """Cria versão em texto simples do email de boas-vindas"""
        role_pt = {
            'admin': 'Administrador',
            'motoboy': 'Motoboy',
            'funcionario': 'Funcionário'
        }.get(role, 'Funcionário')
        
        return f"""
        KAISERHAUS - Bem-vindo à Equipe
        
        Olá, {nome}!
        
        Sua conta foi criada com sucesso no sistema Kaiserhaus.
        
        INFORMAÇÕES DA SUA CONTA:
        Nome: {nome}
        Email: {email}
        Cargo: {role_pt}
        Data de criação: {self._get_current_time()}
        
        CREDENCIAIS DE ACESSO:
        Email: {email}
        Senha Temporária: {senha_temporaria}
        
        Para sua segurança, recomendamos que você altere sua senha no primeiro acesso.
        
        COMO ACESSAR:
        1. Acesse: {login_url}
        2. Faça login com suas credenciais
        3. Vá em "Esqueci minha senha" para definir uma nova senha
        
        IMPORTANTE:
        - Guarde suas credenciais em local seguro
        - Não compartilhe sua senha com ninguém
        - Recomendamos alterar a senha temporária no primeiro acesso
        
        Este é um email automático, não responda.
        
        KAISERHAUS
        © 2024 Kaiserhaus - Todos os direitos reservados
        Há mais de 40 anos em São Paulo
        """

email_service = EmailService()
