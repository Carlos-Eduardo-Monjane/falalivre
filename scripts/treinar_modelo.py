import os
import sys
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Configurações
IMG_SIZE = 128
BATCH_SIZE = 32
EPOCHS = 10

# Caminhos
TRAIN_DIR = "dataset/training"
VAL_DIR = "dataset/validation"
MODEL_DIR = "../frontend/modelo_alfabeto"

def contar_classes():
    """Conta quantas classes realmente existem"""
    classes = [d for d in os.listdir(TRAIN_DIR) if os.path.isdir(os.path.join(TRAIN_DIR, d))]
    return sorted(classes)

def criar_modelo(num_classes):
    """Cria modelo CNN para reconhecimento de letras"""
    model = models.Sequential([
        # Primeira camada convolucional
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_SIZE, IMG_SIZE, 3)),
        layers.MaxPooling2D((2, 2)),
        layers.BatchNormalization(),
        
        # Segunda camada
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.BatchNormalization(),
        
        # Terceira camada
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.BatchNormalization(),
        
        # Quarta camada
        layers.Conv2D(256, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.BatchNormalization(),
        
        # Flatten e camadas densas
        layers.Flatten(),
        layers.Dropout(0.5),
        layers.Dense(512, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(256, activation='relu'),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model

def carregar_dados():
    """Carrega e pré-processa as imagens"""
    # Data augmentation para treino
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    # Apenas rescale para validação
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    # Carregar imagens
    train_generator = train_datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=True
    )
    
    val_generator = val_datagen.flow_from_directory(
        VAL_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )
    
    return train_generator, val_generator

def treinar_modelo():
    """Treina e salva o modelo"""
    print("📊 Carregando dados...")
    train_generator, val_generator = carregar_dados()
    
    num_classes = len(train_generator.class_indices)
    print(f"\n✅ Classes encontradas: {list(train_generator.class_indices.keys())}")
    print(f"📊 Total de classes: {num_classes}")
    print(f"📈 Total de imagens de treino: {train_generator.samples}")
    print(f"📉 Total de imagens de validação: {val_generator.samples}")
    
    print("\n🏗️ Criando modelo...")
    model = criar_modelo(num_classes)
    
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Callbacks
    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=3),
        tf.keras.callbacks.ModelCheckpoint(
            'melhor_modelo.keras',
            save_best_only=True,
            monitor='val_accuracy'
        )
    ]
    
    print("\n🚀 Iniciando treinamento...")
    history = model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=val_generator,
        callbacks=callbacks,
        verbose=1
    )
    
    # Salvar modelo
    os.makedirs(MODEL_DIR, exist_ok=True)
    model.save(os.path.join(MODEL_DIR, 'modelo_alfabeto.keras'))
    
    # Salvar mapeamento de classes
    with open(os.path.join(MODEL_DIR, 'class_indices.json'), 'w') as f:
        json.dump(train_generator.class_indices, f)
    
    print(f"\n✅ Modelo salvo em {MODEL_DIR}/")
    
    # Avaliação final
    test_loss, test_acc = model.evaluate(val_generator)
    print(f"\n📊 Acurácia na validação: {test_acc:.2%}")
    
    # Mostrar histórico
    print(f"\n📈 Histórico de treinamento:")
    print(f"   Melhor acurácia de treino: {max(history.history['accuracy']):.2%}")
    print(f"   Melhor acurácia de validação: {max(history.history['val_accuracy']):.2%}")
    
    return model, history

if __name__ == "__main__":
    print("🎯 TREINAMENTO DE RECONHECIMENTO DE ALFABETO MANUAL")
    print("=" * 50)
    
    # Verificar se as pastas existem
    if not os.path.exists(TRAIN_DIR):
        print(f"\n❌ Pasta {TRAIN_DIR} não encontrada!")
        print("Execute primeiro: python scripts/organizar_dataset.py")
        sys.exit(1)
    
    treinar_modelo()
    print("\n🎉 Modelo treinado e salvo com sucesso!")