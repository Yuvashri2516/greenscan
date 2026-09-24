import json
import tensorflow as tf

model_path = r"C:\Greenscan project\model\greenscan_model.keras"
model = tf.keras.models.load_model(model_path)
print("=== MODEL SUMMARY ===")
model.summary()
print("\n=== INPUT SHAPE ===")
print("Input shape:", model.input_shape)
print("Output shape:", model.output_shape)
print("\n=== LAYERS ===")
for i, layer in enumerate(model.layers):
    print(f"Layer {i}: {layer.name} ({layer.__class__.__name__}), trainable={layer.trainable}")
    if hasattr(layer, 'layers'):
        print(f"  Sublayers in {layer.name}: {len(layer.layers)}")
        trainable_sub = sum(1 for l in layer.layers if l.trainable)
        print(f"  Trainable sublayers: {trainable_sub}/{len(layer.layers)}")

print("\n=== OPTIMIZER & LOSS ===")
if hasattr(model, 'optimizer') and model.optimizer:
    print("Optimizer:", model.optimizer.__class__.__name__)
    print("Learning rate:", getattr(model.optimizer, 'learning_rate', None))
    if hasattr(model.optimizer, 'learning_rate'):
        lr = model.optimizer.learning_rate
        if hasattr(lr, 'numpy'):
            print("LR value:", lr.numpy())
        else:
            print("LR:", lr)
print("Loss:", getattr(model, 'loss', None))
