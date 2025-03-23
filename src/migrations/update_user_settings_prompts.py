from src.utils.database import execute_query

def update_user_settings_prompts():
    """Atualiza a tabela user_settings adicionando campos para prompts específicos de rede social."""
    
    # Primeiro, verificar se a coluna custom_prompt existe
    check_query = """
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name='user_settings' AND column_name='custom_prompt'
    );
    """
    
    result = execute_query(check_query, fetchone=True)
    has_custom_prompt = result.get('exists', False)
    
    if has_custom_prompt:
        # Adicionar as novas colunas
        add_columns_query = """
        ALTER TABLE user_settings 
        ADD COLUMN IF NOT EXISTS instagram_prompt TEXT,
        ADD COLUMN IF NOT EXISTS tiktok_prompt TEXT;
        """
        
        execute_query(add_columns_query)
        print("Colunas instagram_prompt e tiktok_prompt adicionadas com sucesso.")
        
        # Copiar dados de custom_prompt para os novos campos se existirem
        copy_data_query = """
        UPDATE user_settings 
        SET instagram_prompt = custom_prompt, 
            tiktok_prompt = custom_prompt
        WHERE custom_prompt IS NOT NULL;
        """
        
        execute_query(copy_data_query)
        print("Dados migrados de custom_prompt para os novos campos.")
        
        # Remover a coluna antiga
        # drop_column_query = """
        # ALTER TABLE user_settings DROP COLUMN IF EXISTS custom_prompt;
        # """
        
        # execute_query(drop_column_query)
        # print("Coluna custom_prompt removida com sucesso.")
    else:
        # Se não existir, apenas criar as novas colunas
        add_columns_query = """
        ALTER TABLE user_settings 
        ADD COLUMN IF NOT EXISTS instagram_prompt TEXT,
        ADD COLUMN IF NOT EXISTS tiktok_prompt TEXT;
        """
        
        execute_query(add_columns_query)
        print("Colunas instagram_prompt e tiktok_prompt adicionadas com sucesso.")
    
    print("Migração de prompts concluída com sucesso.")
    
if __name__ == "__main__":
    update_user_settings_prompts() 