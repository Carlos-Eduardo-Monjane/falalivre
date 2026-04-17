import os
import shutil
import random
from pathlib import Path

# Configurações
DATASET_ORIGINAL = "dataset/raw"
DATASET_TRAINING = "dataset/training"
DATASET_VALIDATION = "dataset/validation"

LETRAS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
          'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

def criar_estrutura():
    """Cria as pastas necessárias"""
    for letra in LETRAS:
        os.makedirs(os.path.join(DATASET_TRAINING, letra), exist_ok=True)
        os.makedirs(os.path.join(DATASET_VALIDATION, letra), exist_ok=True)
    print("✅ Estrutura de pastas criada")

def organizar_imagens(percentual_validacao=0.2):
    """Organiza as imagens nas pastas de treino e validação"""
    total_imagens = 0
    
    for letra in LETRAS:
        pasta_origem = os.path.join(DATASET_ORIGINAL, letra)
        
        if not os.path.exists(pasta_origem):
            print(f"⚠️ Pasta {letra} não encontrada em {DATASET_ORIGINAL}")
            continue
        
        imagens = [f for f in os.listdir(pasta_origem) 
                   if f.endswith(('.png', '.jpg', '.jpeg'))]
        
        if not imagens:
            print(f"⚠️ Nenhuma imagem para letra {letra}")
            continue
        
        random.shuffle(imagens)
        total = len(imagens)
        validacao_count = int(total * percentual_validacao)
        
        # Limpar pastas de destino
        treino_destino = os.path.join(DATASET_TRAINING, letra)
        valid_destino = os.path.join(DATASET_VALIDATION, letra)
        
        for f in os.listdir(treino_destino):
            os.remove(os.path.join(treino_destino, f))
        for f in os.listdir(valid_destino):
            os.remove(os.path.join(valid_destino, f))
        
        # Copiar para validação
        for img in imagens[:validacao_count]:
            src = os.path.join(pasta_origem, img)
            dst = os.path.join(valid_destino, img)
            shutil.copy2(src, dst)
        
        # Copiar para treino
        for img in imagens[validacao_count:]:
            src = os.path.join(pasta_origem, img)
            dst = os.path.join(treino_destino, img)
            shutil.copy2(src, dst)
        
        print(f"✅ Letra {letra}: {total - validacao_count} treino, {validacao_count} validação")
        total_imagens += total
    
    print(f"\n📊 Total de imagens processadas: {total_imagens}")

if __name__ == "__main__":
    print("=" * 50)
    print("📁 ORGANIZADOR DE DATASET")
    print("=" * 50)
    
    criar_estrutura()
    
    if not os.path.exists(DATASET_ORIGINAL):
        print(f"\n❌ Pasta {DATASET_ORIGINAL} não encontrada!")
        print("Por favor, crie a estrutura:")
        print("dataset/raw/A/")
        print("dataset/raw/B/")
        print("...")
    else:
        organizar_imagens()
        print("\n🎉 Dataset organizado com sucesso!")